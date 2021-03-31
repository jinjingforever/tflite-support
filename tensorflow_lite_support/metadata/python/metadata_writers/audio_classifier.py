# Copyright 2021 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Writes metadata and label file to the audio classifier models."""

from typing import List, Optional

from tensorflow_lite_support.metadata.python.metadata_writers import metadata_info
from tensorflow_lite_support.metadata.python.metadata_writers import metadata_writer
from tensorflow_lite_support.metadata.python.metadata_writers import writer_utils

_MODEL_NAME = "AudioClassifier"
_MODEL_DESCRIPTION = (
    "Identify the most prominent type in the audio clip from a known set of "
    "categories.")
_INPUT_NAME = "audio_clip"
_INPUT_DESCRIPTION = "Input audio clip to be classified."
_OUTPUT_NAME = "probability"
_OUTPUT_DESCRIPTION = "Scores of the labels respectively."
_AUDIO_TENSOR_INDEX = 0


class MetadataWriter(metadata_writer.MetadataWriter):
  """Writes metadata into an audio classifier."""

  @classmethod
  def create_from_metadata_info(
      cls,
      model_buffer: bytearray,
      general_md: Optional[metadata_info.GeneralMd] = None,
      input_md: Optional[metadata_info.InputAudioTensorMd] = None,
      output_md: Optional[metadata_info.ClassificationTensorMd] = None):
    """Creates MetadataWriter based on general/input/output information.

    Args:
      model_buffer: valid buffer of the model file.
      general_md: general infromation about the model. If not specified, default
        general metadata will be generated.
      input_md: input audio tensor informaton, if not specified, default input
        metadata will be generated.
      output_md: output classification tensor informaton, if not specified,
        default output metadata will be generated.

    Returns:
      A MetadataWriter object.
    """

    if general_md is None:
      general_md = metadata_info.GeneralMd(
          name=_MODEL_NAME, description=_MODEL_DESCRIPTION)

    if input_md is None:
      input_md = metadata_info.InputAudioTensorMd(
          name=_INPUT_NAME, description=_INPUT_DESCRIPTION)

    if output_md is None:
      output_md = metadata_info.ClassificationTensorMd(
          name=_OUTPUT_NAME, description=_OUTPUT_DESCRIPTION)

    output_md.associated_files = output_md.associated_files or []

    return super().create_from_metadata_info(
        model_buffer=model_buffer,
        general_md=general_md,
        input_md=[input_md],
        output_md=[output_md],
        associated_files=[
            file.file_path for file in output_md.associated_files
        ])

  @classmethod
  def create_for_inference(
      cls,
      model_buffer: bytearray,
      sample_rate: int,
      channels: int,
      min_required_samples: int,
      label_file_paths: List[str],
      score_calibration_md: Optional[metadata_info.ScoreCalibrationMd] = None):
    """Creates mandatory metadata for TFLite Support inference.

    The parameters required in this method are mandatory when using TFLite
    Support features, such as Task library and Codegen tool (Android Studio ML
    Binding). Other metadata fields will be set to default. If other fields need
    to be filled, use the method `create_from_metadata_info` to edit them.

    Args:
      model_buffer: valid buffer of the model file.
      sample_rate: the sample rate in Hz when the audio was captured.
      channels: the channel count of the audio.
      min_required_samples: the minimum required number of per-channel samples
        in order to run inference properly. Optional for fixed-size audio
        tensors and default to 0. The minimum required flat size of the audio
        tensor is min_required_samples x channels.
      label_file_paths: paths to the label files [1] in the classification
        tensor. Pass in an empty list if the model does not have any label file.
      score_calibration_md: information of the score calibration operation [2]
        in the classification tensor. Optional if the model does not use score
        calibration.
      [1]:
        https://github.com/tensorflow/tflite-support/blob/b80289c4cd1224d0e1836c7654e82f070f9eefaa/tensorflow_lite_support/metadata/metadata_schema.fbs#L95
      [2]:
        https://github.com/tensorflow/tflite-support/blob/5e0cdf5460788c481f5cd18aab8728ec36cf9733/tensorflow_lite_support/metadata/metadata_schema.fbs#L434

    Returns:
      A MetadataWriter object.

    Raises:
      ValueError: if either sample_rate or channels is non-positive, or if
        min_required_samples is negative.
      ValueError: if min_required_samples is 0, but the input audio tensor is
        not fixed-size.
    """
    # To make Task Library working properly, sample_rate, channels,
    # min_required_samples need to be positive.
    if sample_rate <= 0:
      raise ValueError(
          "sample_rate should be positive, but got {}.".format(sample_rate))

    if channels <= 0:
      raise ValueError(
          "channels should be positive, but got {}.".format(channels))

    if min_required_samples < 0:
      raise ValueError(
          "min_required_samples should be non-negative, but got {}.".format(
              min_required_samples))

    if min_required_samples == 0:
      tensor_shape = writer_utils.get_input_tensor_shape(
          model_buffer, _AUDIO_TENSOR_INDEX)

      # The dynamic size input shape can be an empty array or arrays like [1]
      # and [1, 1], where the flat size is 1.
      flat_size = writer_utils.compute_flat_size(tensor_shape)
      if not tensor_shape or flat_size == 1:
        raise ValueError(
            "The audio tensor is not fixed-size, therefore min_required_samples"
            "is required, and should be a positive value.")
      # Update min_required_samples if the audio tensor is fixed-size using
      # ceiling division.
      min_required_samples = (flat_size + channels - 1) // channels

    input_md = metadata_info.InputAudioTensorMd(_INPUT_NAME, _INPUT_DESCRIPTION,
                                                sample_rate, channels,
                                                min_required_samples)

    output_md = metadata_info.ClassificationTensorMd(
        name=_OUTPUT_NAME,
        description=_OUTPUT_DESCRIPTION,
        label_files=[
            metadata_info.LabelFileMd(file_path=file_path)
            for file_path in label_file_paths
        ],
        tensor_type=writer_utils.get_output_tensor_types(model_buffer)[0],
        score_calibration_md=score_calibration_md)

    return cls.create_from_metadata_info(
        model_buffer, input_md=input_md, output_md=output_md)
