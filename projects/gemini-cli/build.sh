#!/bin/bash -eu
cd $SRC/gemini-cli
compile_javascript_fuzzer . fuzzers/fuzz_proxy_security.js --sync
