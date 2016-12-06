
import PV_analysis
import semiconductor
import traceback
import os


class Error_handel():

    folder = dir_path = os.path.dirname(os.path.realpath(__file__))

    def write(self, err, region):

        s = '-----------------------------------\n\nthe versions are:\n'
        s += '\tPV_analysis:\t' + PV_analysis.__version__ + '\n'
        s += '\tsemiconductor:\t' + semiconductor.__version__ + '\n'
        s += '---------\n'

        with open(os.path.join(self.folder, 'log.txt'), mode='a') as f:
            print('error written')
            f.write(s)
            traceback.print_exc(file=f)
            f.write(str(err))
            f.write(' in the ' + region)
            f.write('\n-----------------------------\n')
