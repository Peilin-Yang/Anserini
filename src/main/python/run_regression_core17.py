import sys
import os
import argparse

from subprocess import call

index_cmd = """
nohup sh target/appassembler/bin/IndexCollection -collection NewYorkTimesCollection \
 -input /tuna1/collections/newswire/NYTcorpus.uncompressed/data/ -generator JsoupGenerator \
 -index lucene-index.nyt.pos+docvectors+rawdocs -threads 16 \
 -storePositions -storeDocvectors -storeRawDocs -optimize"""

run_cmds = [ \
    "nohup sh target/appassembler/bin/SearchCollection -topicreader Trec -index lucene-index.nyt.pos+docvectors+rawdocs -topics src/main/resources/topics-and-qrels/topics.core17.txt -output run.core17.bm25.txt -bm25",
    "nohup sh target/appassembler/bin/SearchCollection -topicreader Trec -index lucene-index.nyt.pos+docvectors+rawdocs -topics src/main/resources/topics-and-qrels/topics.core17.txt -output run.core17.bm25+rm3.txt -bm25 -rm3",
    "nohup sh target/appassembler/bin/SearchCollection -topicreader Trec -index lucene-index.nyt.pos+docvectors+rawdocs -topics src/main/resources/topics-and-qrels/topics.core17.txt -output run.core17.ql.txt -ql",
    "nohup sh target/appassembler/bin/SearchCollection -topicreader Trec -index lucene-index.nyt.pos+docvectors+rawdocs -topics src/main/resources/topics-and-qrels/topics.core17.txt -output run.core17.ql+rm3.txt -ql -rm3"]

qrels = "src/main/resources/topics-and-qrels/qrels.core17.txt"

def extract_value_from_doc(key, row, col):
    return float(os.popen("grep '{}' docs/experiments-core17.md | head -{} | tail -1".format(key, row)).read().split('|')[col].strip())

def trec_eval_metric(metric, qrels, run):
    return float(os.popen("eval/trec_eval.9.0/trec_eval -m {} {} {}".format(metric, qrels, run)).read().split("\t")[2].strip())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run regression tests on CORE17.')
    parser.add_argument('--index', dest='index', action='store_true', help='rebuild index from scratch')

    args = parser.parse_args()

    # Decide if we're going to index from scratch. If not, use pre-stored index at known location.
    if args.index == True:
        call(index_cmd, shell=True)
        index_path = 'lucene-index.nyt.pos+docvectors+rawdocs'
        print(args.index)
    else:
        index_path = '/tuna1/indexes/lucene-index.nyt.pos+docvectors+rawdocs'

    # Use the correct index path.
    for cmd in run_cmds:
        call(cmd.format(index_path), shell=True)

    expected_map = extract_value_from_doc("All Topics", 1, 1)
    actual_map = trec_eval_metric("map", qrels, "run.core17.bm25.txt")
    print("All Topics: bm25     : map : %.4f %.4f" % (expected_map, actual_map) + ('  !' if expected_map != actual_map else ''))
    expected_map = extract_value_from_doc("All Topics", 1, 2)
    actual_map = trec_eval_metric("map", qrels, "run.core17.bm25+rm3.txt")
    print("All Topics: bm25+rm3 : map : %.4f %.4f" % (expected_map, actual_map) + ('  !' if expected_map != actual_map else ''))
    expected_map = extract_value_from_doc("All Topics", 1, 3)
    actual_map = trec_eval_metric("map", qrels, "run.core17.ql.txt")
    print("All Topics: ql       : map : %.4f %.4f" % (expected_map, actual_map) + ('  !' if expected_map != actual_map else ''))
    expected_map = extract_value_from_doc("All Topics", 1, 4)
    actual_map = trec_eval_metric("map", qrels, "run.core17.ql+rm3.txt")
    print("All Topics: ql+rm3   : map : %.4f %.4f" % (expected_map, actual_map) + ('  !' if expected_map != actual_map else ''))

    expected_p30 = extract_value_from_doc("All Topics", 2, 1)
    actual_p30 = trec_eval_metric("P.30", qrels, "run.core17.bm25.txt")
    print("All Topics: bm25     : p30 : %.4f %.4f" % (expected_p30, actual_p30) + ('  !' if expected_p30 != actual_p30 else ''))
    expected_p30 = extract_value_from_doc("All Topics", 2, 2)
    actual_p30 = trec_eval_metric("P.30", qrels, "run.core17.bm25+rm3.txt")
    print("All Topics: bm25+rm3 : p30 : %.4f %.4f" % (expected_p30, actual_p30) + ('  !' if expected_p30 != actual_p30 else ''))
    expected_p30 = extract_value_from_doc("All Topics", 2, 3)
    actual_p30 = trec_eval_metric("P.30", qrels, "run.core17.ql.txt")
    print("All Topics: ql       : p30 : %.4f %.4f" % (expected_p30, actual_p30) + ('  !' if expected_p30 != actual_p30 else ''))
    expected_p30 = extract_value_from_doc("All Topics", 2, 4)
    actual_p30 = trec_eval_metric("P.30", qrels, "run.core17.ql+rm3.txt")
    print("All Topics: ql+rm3   : p30 : %.4f %.4f" % (expected_p30, actual_p30) + ('  !' if expected_p30 != actual_p30 else ''))
