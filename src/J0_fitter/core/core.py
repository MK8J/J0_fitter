
import collections as col
import IO
import sys
import numpy as np

sys.path.append(r'D:\Dropbox\CommonCode\analysis\src')
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

        if isinstance(self.ltc.sample.ni_eff, np.ndarray):
            if self.ltc.sample.ni_eff.shape == self.nxc.shape:
                self.ltc.sample.ni_eff = self.ltc.sample.ni_eff[maxindex:]

        self.nxc = self.nxc[maxindex:]
        self.ltc.tau = self.tau[maxindex:]
        self.ltc.gen = self.gen[maxindex:]
        if isinstance(self.ltc.intrinsic_tau, np.ndarray):
            self.ltc.intrinsic_tau = self.ltc.intrinsic_tau[maxindex:]

    @property
    def nxc(self):
        return self.ltc.sample.nxc

    @nxc.setter
    def nxc(self, value):
        self.ltc.sample.nxc = value

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
    def fitting_width(self, value):
        self._fitting_width = value

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
    def optical_constant(self):
        return self.ltc.sample.absorptance

    @optical_constant.setter
    def optical_constant(self, value):
        self.ltc.sample.absorptance = float(value)

    @property
    def thickness(self):
        return self.ltc.sample.thickness

    @thickness.setter
    def thickness(self, value):
        self.ltc.sample.thickness = value

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

    @property
    def mobility_sum(self):
        return self.ltc.mobility_sum

    @mobility_sum.setter
    def mobility_sum(self, value):
        self.ltc.mobility_sum = ''
        self.ltc.mobility_model = value

    @property
    def D_ambi(self):

        try:
            _D_ambi = self.ltc.D_ambi[self.fitting_mask]
        except:
            _D_ambi = self.ltc.D_ambi
        return _D_ambi

    def J0(self, method):
        '''
        determines the J0, using the provided method for the current sample
        '''
        self.method = method
        # if an index is provided, use it
        if np.all(self.fitting_mask) is None:
            self.fitting_mask = np.ones(self.nxc.shape[0])

        _ni = self.ltc.sample.ni
        _ni_eff = self.ltc.sample.ni_eff

        # if ni is an array, mask it
        if isinstance(_ni_eff, np.ndarray
                      ) and _ni_eff.shape[0] == self.nxc.shape[0]:
            _ni_eff = _ni_eff[self.fitting_mask]

        # print(_ni.shape, _ni_eff.shape, self.tau[self.fitting_mask].shape,
        #       self.ltc.intrinsic_tau[self.fitting_mask].shape, self.tau.shape,
        #       self.fitting_mask.shape)

        self._J0 = J0(nxc=self.nxc[self.fitting_mask],
                      tau=self.tau[self.fitting_mask],
                      thickness=self.thickness,
                      ni=_ni, method=method,
                      ni_eff=_ni_eff,
                      tau_aug=self.ltc.intrinsic_tau[self.fitting_mask],
                      Ndop=self.ltc.sample.doping,
                      D_ambi=self.D_ambi)

        return self._J0

    def _calculate_lifetime(self, dark_voltage):
        self.ltc.cal_lifetime(analysis='generalised',
                              dark_voltage=dark_voltage)

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
                'center value {0:.2e} was increased'.format(self.nxc_fit_center) +
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

        self.MDC_analysis_type = {
            'At fixed MCD':  self.get_J0_fixed_nxc,
            'At each MCD': self.get_J0_nxc_scan,
        }

        self.settings = settings
        self.analysis = analysis

        # print('\ndata_handeller inputs:')
        # print('\t', self.settings)
        # print('\t', self.analysis)

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

    def get_J0_fixed_nxc(self):
        '''
        returns a nested dictionary of sample name, J0 method, and finially the
        determined value.  Yes it's dictionaries all the way down.
        '''
        samples = {}
        i = 0
        while self.data.isFilesLeft():
            self.data.nextFile()
            self._use_external_models()
            self._use_external_nxc_calcs()
            self.data.mask()
            wafer, i = self._get_J0(i)
            samples.update(wafer)
            print('sample {0} done! {1:.2e} A/cm^-2'.format(
                self.data.sample_name, wafer[i]['J0']))

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
            self._use_external_models()
            self._use_external_nxc_calcs()

            for nxc in self.data.nxc_in_fitting_range():
                self.data.nxc_fit_center = nxc
                self.data.mask()

                wafer, i = self._get_J0(i)
                samples.update(wafer)
            # print(wafer[i]['Sample name'] + 'Done')
        return samples

    def test(self):
        print(self.settings)
        print(self.analysis)

    def go(self):
        '''
        A controller that sends us in the right direction for determining J0
        '''
        # if not using sinton values, update them in the class

        if self.analysis['analysis_MCD'] in self.MDC_analysis_type.keys():

            J0_dic = self.MDC_analysis_type[self.analysis['analysis_MCD']]()
        else:
            print('MCD analysis not a valid option')

        # A check that the dic is not empty
        if J0_dic:
            IO.save('Summary', J0_dic)

        pass

    def _use_external_nxc_calcs(self):
        '''
        If use_sinton_values == False,
        Recaculates nxc from the photoconductance
        '''
        if not self.settings['use_sinton_values']:

            self.data._calculate_lifetime(
                self.data.ltc.dark_voltage)

    def _use_external_models(self):
        '''
        If use_sinton_values == False,
        Applied the values and models provided from the GUI
        to caculate J0.
        '''
        if not self.settings['use_sinton_values']:

            settings = dict(self.settings)
            del settings['use_sinton_values']

            if 'ni' in settings.keys():
                self._set_models({'ni': settings.pop('ni')})

            self._set_models(settings)

    def _set_models(self, settings):
            # things that can be updated
        for key in settings.keys():

            if hasattr(self.data, key):
                print('data has key', key, settings[key])
                setattr(self.data, key, settings[key])

            elif hasattr(self.data.ltc, key):
                print('data.ltc has key', key)
                setattr(self.data.ltc, key, settings[key])

            elif hasattr(self.data.ltc.sample, key):
                print('data.ltc.sample has key', key)
                setattr(self.data.ltc.sample, key, settings[key])

            else:
                print('\t', key, 'not and attribute',
                      hasattr(self.data, key))
