#!/bin/bash

set -e

REPORT_DIR="reports"
mkdir -p "$REPORT_DIR"

run() {
  FILE="$1"
  NAME=$(basename "$FILE")
  NAME_NO_EXT="${NAME%.*}"

  if [[ $NAME_NO_EXT == ising_* || $NAME_NO_EXT == *n26* || $NAME_NO_EXT == *n29* || $NAME_NO_EXT == *n30* ]]; then
    echo "Skipping $NAME_NO_EXT (too heavy)"
    echo "----------------------------------"
    return
  fi

  echo "Running $NAME..."

  if [[ $NAME_NO_EXT == *route* || $NAME_NO_EXT == *routing* || $NAME_NO_EXT == *swap* || $NAME_NO_EXT == *stress* ]]; then
    python3 analyzer/quantum_security_analyzer.py \
      --input "$FILE" \
      --coupling-map 0-1,1-2,2-3,3-4,4-5,5-6,6-7 \
      --noise-model heavy

  elif [[ $NAME_NO_EXT == *sdk* ]]; then
    python3 analyzer/quantum_security_analyzer.py \
      --input "$FILE" \
      --noise-model light

  elif [[ $NAME_NO_EXT == *anom* || $NAME_NO_EXT == llm_* ]]; then
    python3 analyzer/quantum_security_analyzer.py \
      --input "$FILE" \
      --noise-model heavy

  else
    python3 analyzer/quantum_security_analyzer.py \
      --input "$FILE" \
      --noise-model light
  fi

  echo "Saved -> $REPORT_DIR/$NAME_NO_EXT.json"
  echo "----------------------------------"
}

for file in circuits/*.py circuits/*.qasm; do
  run "$file"
done

echo "All circuits processed."