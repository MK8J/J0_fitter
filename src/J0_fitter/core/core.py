
import collections as col
import IO
import sys
import numpy as np

# sys.path.append(r'D:\Dropbox\CommonCode\analysis\src')
# sys.path.append(r'D:\Dropbox\CommonCode\semiconductor\src')

import PV_analysis.lifetime.determine.J0 as J0
from semiconductor.material import IntrinsicCarrierDensity as ni_

# import matplotlib.pylab as plt


class data_list():

    files = []
    data = []

    # a mask to hide data for J0 fitting
    _nxc_fit_center = None  # the centering of a fitting mask
    _fitting_width = None  # the fitting width as a decimal
    fitting_mask = np.array([None])

    def __init__(self, files):
        if len(files) > 0:
            self.files = col.deque(files)

    def isFilesLeft(self):
        return len(self.files) >= 1

    def nextFile(self):

        if len(self.files) > 0:
            fname = self.files.popleft()

            self.ltc = IO.load(fname)
            self._remove_data_after_peak()
        else:
            fname = None
            self.ltc = None

    def _remove_data_after_peak(self):

        maxindex = self.nxc.argmax()

        self.ltc.nxc = self.nxc[maxindex:]
        self.ltc.tau = self.tau[maxindex:]
        self.ltc.gen = self.gen[maxindex:]
        if isinstance(self.ltc.auger, np.ndarray):
            self.ltc.auger = self.ltc.auger[maxindex:]
        if isinstance(self.ltc.ni, np.ndarray):
            self.ltc.ni = self.ltc.ni[maxindex:]

    @property
    def nxc(self):
        return self.ltc.nxc

    @property
    def nxc_fit_center(self):
        return self._nxc_fit_center or self.ltc.other_inf['MCD']

    @nxc_fit_center.setter
    def nxc_fit_center(self, value):
        self._nxc_fit_center = value

    @property
    def fitting_width(self):
        return self._fitting_width or self.ltc.other_inf[
            'Fit Range']

    @fitting_width.setter
    def fitting_width(self):
        self._fitting_width

    @property
    def gen(self):
        return self.ltc.gen

    @property
    def tau(self):
        return self.ltc.tau

    @property
    def sample_name(self):
        try:
            # is the name is a byte
            name = self.ltc.sample.name.decode("utf-8")
        except:
            name = self.ltc.sample.name
        return name

    @property
    def doping(self):
        return self.ltc.sample.doping

    @property
    def thickness(self):
        return self.ltc.sample.thickness

    @property
    def inf(self):
        '''
        Returns a dictionary with "relevant" information about the sample
        '''
        dic = col.OrderedDict({})
        dic['Sample name'] = self.sample_name
        dic['MCD analysised'] = self.nxc_fit_center
        dic['Fit range'] = self.fitting_width
        dic['Jo fitting method'] = self.method
        dic['J0'] = self._J0

        return dic

    def J0(self, method):
        '''
        determines the J0, using the provided method for the current sample
        '''
        self.method = method
        # if an index is provided, use it
        if np.all(self.fitting_mask) is None:
            self._J0 = J0(nxc=self.nxc, tau=self.tau,
                          thickness=self.thickness,
                          ni=self.ltc.ni_eff, method=method,
                          tau_aug=self.ltc.auger,
                          Ndop=self.doping)
        else:
            try:
                _ni = self.ltc.ni_eff[self.fitting_mask]
            except:
                _ni = self.ltc.ni_eff
            self._J0 = J0(nxc=self.nxc[self.fitting_mask],
                          tau=self.tau[self.fitting_mask],
                          thickness=self.thickness,
                          ni=_ni, method=method,
                          tau_aug=self.ltc.auger[self.fitting_mask],
                          Ndop=self.doping)

        return self._J0

    def _caculate_lifetime(self):
        self.ltc.cal_lifetime()

    def _check_nxc_fit_center(self):

        # remove bad points
        is_finite = np.isfinite(self.nxc)

        if self.nxc_fit_center * (1 + self.fitting_width) > np.amax(self.nxc[is_finite]):
            print(
                'center value {0:.2e} was reduced'.format(self.nxc_fit_center) +
                ', as it was larger than the highest'
                + ' measured excess carrier density')
            self.nxc_fit_center = np.amax(
                self.nxc[is_finite]) * (1 - self.fitting_width)

        elif self.nxc_fit_center * (1. - self.fitting_width) < np.amin(self.nxc[is_finite]):
            print(
                'center value was increase'.format(self.nxc_fit_center) +
                ', as it was smaller than the lowest'
                + ' measured excess carrier density')
            self.nxc_fit_center = np.amin(
                self.nxc[is_finite]) * (1 + self.fitting_width)

    def nxc_in_fitting_range(self):
        '''
        returns a list of nxc in the range where a acceptance center nxc is accepted.
        '''
        test = np.copy(self.nxc)
        index = test < np.amax(test) / (1. + self.fitting_width)
        index *= test > np.amin(test) / (1. - self.fitting_width)
        return test[index]

    def mask(self):
        '''
        creates a mask for the data to which J0 is fit. this functin checks the provided center value is not inside the measured data range
        inputs:
            center: (float, optional)
                The center nxc value of the mask. if a value is not provided the value from the sinton excel is used.
            width: (float, optional)
                the percentage width that the fit range should extend from
                the center. The supplied valule should be as a decimal, i.e. 90% = .90. If a value is not provided the value from the sinton excel is used.
        '''

        self._check_nxc_fit_center()

        self.fitting_mask = self.nxc > self.nxc_fit_center * \
            (1 - self.fitting_width)
        self.fitting_mask *= self.nxc < self.nxc_fit_center * \
            (1 + self.fitting_width)


class data_handeller():

    def __init__(self, settings, analysis):

        self.settings = settings
        self.analysis = analysis

        print('\ndata_handeller inputs:')
        print('\t', self.settings)
        print('\t', self.analysis)

        self._check_inputs()

        self.data = data_list(self.analysis['files'])

    def _check_inputs(self):
        pass

    def _get_J0(self, sample_index):
        '''
        determines J0 for the current file
        '''
        wafer = {}
        for method in self.analysis['analysis_method']:
            sample_index += 1
            self.data.J0(method)
            wafer[sample_index] = self.data.inf

        return wafer, sample_index

    def get_J0(self):
        '''
        returns a nested dictionary of sample name, J0 method, and finially the
        determined value.  Yes it's dictionaries all the way down.
        '''
        samples = {}
        i = 0
        while self.data.isFilesLeft():
            self.data.nextFile()
            self.data.mask()
            wafer, i = self._get_J0(i)
            samples.update(wafer)
            print('sample {0} done! {1:.2e} A/cm^-2'.format(
                self.data.sample_name, wafer[i]['J0']))

        print(samples)
        return samples

    def get_J0_nxc_scan(self):
        '''
        returns a nested dictionary of sample name, J0 method, and finially the
        determined value.  Yes it's dictionaries all the way down.
        '''
        samples = {}
        i = 0
        while self.data.isFilesLeft():
            self.data.nextFile()
            for nxc in self.data.nxc_in_fitting_range():
                self.data.nxc_fit_center = nxc
                self.data.mask()

                wafer, i = self._get_J0(i)
                samples.update(wafer)
            print(wafer[i]['Sample name'] + 'Done')
        return samples
