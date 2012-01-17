#!/bin/bash

date="$1"

# Use getnightly.py to find this build on ftp.mozilla.org
ret=$(./getnightly.py "$date" 2>test_nightly.tmp || true)
if [ -z "$ret" ]; then
  echo "!! $date -- Failed to get nightly: $(cat test_nightly.tmp)"
  rm -rf test_nightly.tmp
  exit 1
fi

{
  read timestamp
  read rev
  read url
} <<< "$ret"
echo ":: $date -- Building: $timestamp, $rev"

# Get full commit ID from repo
fullrev=$(
  cd mozilla-central
  hg pull &>/dev/null
  hg log -r "$rev" --template "{node}" || true
)
if [ -z "$fullrev" ]; then
  echo "!! Couldn't lookup commit info for nightly build $rev"
  exit 1
fi

# Download and extract build
rm -rf firefox
echo ":: Downloading build..."
if ! (curl -# "$url" | tar xj) || [ ! -d "firefox" ]; then
  echo "!! Failed to download build from '$url'"
  exit 1
fi

# Run test
if ! ./slimtest_linux.sh --logfile "logs/$(date +%Y%m%d_%H%M%S)_$rev.log" \
                          --binary firefox/firefox \
                          --buildname "$fullrev" \
                          --buildtime "$timestamp" \
                          --sqlitedb slimtest.sqlite; then
  echo "!! Test failed, see benchtester log for $rev"
fi