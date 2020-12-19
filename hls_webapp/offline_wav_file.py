import hearinglosssimulator as hls
import pyopencl


def compute(in_filename, out_filename, left_p_loss, right_p_loss):
    # this parameters is important
    calibration = 93  # dbSPL for 0dBFs
    # define loss parameters
    loss_params = {'left': {'freqs':  [125., 250., 500., 1000., 2000., 4000., 8000.],
                            'compression_degree': [0., 0., 0., 0., 0., 0., 0.],
                            'passive_loss_db': left_p_loss,
                            },
                   'right': {'freqs':  [125., 250., 500., 1000., 2000., 4000., 8000.],
                             'compression_degree': [0., 0., 0., 0., 0., 0., 0.],
                             'passive_loss_db': right_p_loss,
                             }
                   }
    params = dict(nb_freq_band=32, low_freq=100., high_freq=1000.,
                  tau_level=0.005,  level_step=1., level_max=100.,
                  calibration=calibration,
                  loss_params=loss_params,
                  chunksize=512, backward_chunksize=1024)
    gpu_platform_index = 0  # Put None to manually select
    gpu_device_index = 0  # Put None to manually select
    hls.compute_wave_file(in_filename, out_filename, processing_class=hls.InvComp, duration_limit=10.,
                          gpu_platform_index=gpu_platform_index, gpu_device_index=gpu_device_index,
                          **params)
