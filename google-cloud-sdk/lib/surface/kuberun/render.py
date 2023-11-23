# -*- coding: utf-8 -*- #
# Copyright 2019 Google LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Command to render Kuberun resources to yaml."""
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.kuberun import flags
from googlecloudsdk.command_lib.kuberun import kuberun_command

_DETAILED_HELP = {
    'EXAMPLES':
        """
        To render a KubeRun application to the environment set in gcloud config,
        run:

            $ {command}

        To render a KubeRun application to environment ``ENV'', run:

            $ {command} --environment=ENV
        """,
}


def _OutFlag():
  return flags.StringFlag(
      '--out',
      help='Output directory for rendered resource yaml.',
      required=True)


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Render(kuberun_command.KubeRunCommand, base.ExportCommand):
  """Render KubeRun application to generate the yaml resource configuration."""
  detailed_help = _DETAILED_HELP
  flags = [_OutFlag(), flags.EnvironmentFlag()]

  def Command(self):
    return ['render']
