#!/bin/bash

set -e

REPORT_DIR="reports"
mkdir -p $REPORT_DIR

run() {
  FILE=$1
  NAME=$(basename "$FILE" .py)

  echo "Running $NAME..."

  if [[ $NAME == route_* || $NAME == *routing* || $NAME == *swap* || $NAME == *stress* ]]; then
    CMD="python3 analyzer/quantum_security_analyzer.py \
      --input circuits/$NAME.py \
      --coupling-map 0-1,1-2,2-3,3-4,4-5,5-6,6-7 \
      --noise-model heavy"

  elif [[ $NAME == sdk_* ]]; then
    CMD="python3 analyzer/quantum_security_analyzer.py \
      --input circuits/$NAME.py \
      --noise-model light"

  elif [[ $NAME == anom_* || $NAME == llm_* ]]; then
    CMD="python3 analyzer/quantum_security_analyzer.py \
      --input circuits/$NAME.py \
      --noise-model heavy"

  else
    CMD="python3 analyzer/quantum_security_analyzer.py \
      --input circuits/$NAME.py \
      --noise-model light"
  fi

  #  RUN COMMAND (DO NOT CAPTURE OUTPUT)
  eval $CMD

  echo "Saved -> $REPORT_DIR/$NAME.json"
  echo "----------------------------------"
}

for file in circuits/*.py; do
  run "$file"
done

echo "All circuits processed."