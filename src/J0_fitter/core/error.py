
import PV_analysis
import semiconductor
import traceback


class Error_handel():

    def write(self, err, region):

        s = '-----------------------------------\n\nthe versions are:\n'
        s += '\tPV_analysis:\t' + PV_analysis.__version__ + '\n'
        s += '\tsemiconductor:\t' + semiconductor.__version__ + '\n'
        s += '---------\n'

        with open('log.txt', mode='a') as f:

            f.write(s)
            traceback.print_exc(file=f)
            f.write(str(err))
            f.write(' in the ' + region)
            f.write('\n-----------------------------\n')
