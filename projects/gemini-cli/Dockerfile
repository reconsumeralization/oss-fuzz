# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
################################################################################

# Dockerfile for Gemini CLI OSS-Fuzz Foundation Setup
# Phase 1: Basic Go fuzzing environment

FROM gcr.io/oss-fuzz-base/base-builder

# Install Go
RUN install_go.sh

# Copy project source
COPY . $SRC/gemini-cli/

# Set working directory
WORKDIR $SRC/gemini-cli/

# Verify Go installation
RUN go version

# Print completion message
RUN echo "Foundation Docker environment ready for Gemini CLI Go fuzzing"
