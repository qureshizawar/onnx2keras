import torch
import numpy as np
import onnx
import os

from onnx2keras import onnx_to_keras, check_torch_keras_error

from norm import FNormTest
from clip import FClipTest
from cast import FCastTest
from floor import FFloorTest

if __name__ == '__main__':
    max_error = 0
    for change_ordering in [False, True]:
        for act_type in [
                          FNormTest,
                          FFloorTest,
                          FCastTest,
                          FClipTest
                        ]:
            for i in range(10):
                model = act_type()
                model.eval()

                input_np = np.random.uniform(0, 1, (1, 3, 224, 224))
                input_var = torch.FloatTensor(input_np)

                torch.onnx.export(model, input_var, "_tmpnet.onnx", verbose=True, input_names=['test_in'],
                                  output_names=['test_out'])

                onnx_model = onnx.load('_tmpnet.onnx')
                k_model = onnx_to_keras(onnx_model, ['test_in'], change_ordering=change_ordering)
                os.unlink('_tmpnet.onnx')

                error = check_torch_keras_error(model, k_model, input_np, change_ordering=change_ordering)
                print('Error:', error)
                if max_error < error:
                    max_error = error

    print('Max error: {0}'.format(max_error))
