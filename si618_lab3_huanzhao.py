import mrjob
from mrjob.job import MRJob
import re

WORD_RE = re.compile(r"\b[\w']+\b")#regular expression

class TrigramCount(MRJob):
    OUTPUT_PROTOCOL = mrjob.protocol.RawProtocol
  	# mapper: key _ is always None and ignored

    def mapper(self, _, line):
        words = WORD_RE.findall(line)
        for index, word in enumerate(words):   #index-key, word-value
            if index < len(words) - 2:
                trigram = words[index] + " " + words[index + 1] + " " + words[index + 2]
                yield trigram, 1

    def combiner(self, trigram, counts):
        yield trigram,sum(counts)
        
    def reducer(self, trigram, counts):
        yield trigram, str(sum(counts))

if __name__ == '__main__':
    TrigramCount.run()