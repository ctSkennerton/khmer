#! /usr/bin/env python
#
# This file is part of khmer, http://github.com/ged-lab/khmer/, and is
# Copyright (C) Michigan State University, 2009-2013. It is licensed under
# the three-clause BSD license; see doc/LICENSE.txt.
# Contact: khmer-project@idyll.org
#
import sys
import math
from screed.fasta import fasta_iter
import khmer
import argparse

K = 32
HASHTABLE_SIZE = int(1e9)
N_HT = 4

ABUND_THRESHOLD = 65

parser = argparse.ArgumentParser(
    description="abund-ablate-reads",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("infile")
parser.add_argument("outfile")
args = parser.parse_args()

infile = args.infile
outfile = args.outfile
outfp = open(outfile, 'w')

print 'making hashtable'
ht = khmer.new_counting_hash(K, HASHTABLE_SIZE, N_HT)

print 'eating', infile
ht.consume_fasta(infile)

print 'counting'
for n, record in enumerate(fasta_iter(open(infile))):
    if n % 10000 == 0:
        print>>sys.stderr, '...', n

    seq = record['sequence']
    if len(seq) < K:
        continue

    # ablate end
    pos = len(seq) - K + 1
    while pos >= 0:
        if ht.get(seq[pos:pos + K]) < ABUND_THRESHOLD:
            break
        pos -= 1

    if pos == -1:
        continue

    seq = seq[:pos + K]

    # ablate beginning
    pos = 0
    while pos < len(seq) - K + 1:
        if ht.get(seq[pos:pos + K]) < ABUND_THRESHOLD:
            break
        pos += 1

    if pos == len(seq) - K + 1:
        continue

    seq = seq[pos:]

    if ht.get_max_count(seq) >= ABUND_THRESHOLD:
        continue

    # save!
    print >>outfp, '>%s\n%s' % (record['name'], seq)
