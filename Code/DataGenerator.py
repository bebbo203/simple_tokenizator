import torch.nn as nn
import torch
import codecs


class DataGenerator(torch.utils.data.IterableDataset):

    def __init__(self, path, sentences_max_length, tensor=True, monograms=False):
        self.file = self.open_file(path)
        self.sentences_max_length_computed = self.longest_sentence_size()
        self.tensor = tensor
        self.monograms = monograms
        self.threshold = 150

        if(sentences_max_length == 0):
            self.sentences_max_length = self.sentences_max_length_computed
        else:
            self.sentences_max_length = sentences_max_length
        
        self.freq_dict = self.frequencies_dict()

        if(self.monograms == False):
            self.chars_dict = self.create_chars_dict_bigrams()
        else:
            self.chars_dict = self.create_chars_dict()
        

            
        
    
    def __iter__(self):
        #n_words_in_sentence * one_hot_encoding_dim 
        
        if(self.tensor == False):  
                   
            for _line in self.file.readlines():
                line = _line
                for start in range(0, len(line), self.sentences_max_length):
                    reduced = line[start:start+self.sentences_max_length]
                    yield reduced
        else:   
            if(self.monograms):
                for _line in self.file.readlines():
                    line = _line
                    for c in range(len(line)):
                        if(line[c] in self.chars_dict.keys()):
                            out = torch.zeros(self.sentences_max_length, len(self.chars_dict))
                            out[0][self.chars_dict[line[c]]] = 1
                        yield out.flatten().view(self.sentences_max_length * len(self.chars_dict))
            else:
                for _line in self.file.readlines():
                    line = _line
                    for c in range(len(line)-1):
                        bigram = str(line[c] + line[c+1])
                        
                        if(bigram in self.chars_dict.keys()):
                            out = torch.zeros(self.sentences_max_length, len(self.chars_dict))
                            out[0][self.chars_dict[bigram]] = 1
                        yield out.flatten().view(self.sentences_max_length * len(self.chars_dict))
                            

             

    def open_file(self, path):
        file = open(path, "r", encoding="utf-8")
        return file

    def longest_sentence_size(self):
        M = 0
        for line in self.file.readlines():
            M += len(line)
        self.file.seek(0)
        return M

    def avg_sentence_size(self):
        M = 0
        i = 0
        for line in self.file.readlines():
            M += len(line)
            i += 1
        self.file.seek(0)
        return int(M/i)
    
    def get_dictionary_size(self):
        return len(self.chars_dict)

    def get_sentences_max_length(self):
        return self.sentences_max_length
    
    def create_chars_dict_bigrams(self):
        ret_dict = {}
        for sentence in self.file.readlines():
            for i in range(len(sentence)-1):
                if(sentence[i] != '\n'):
                    bigram = str(sentence[i] + sentence[i+1])
                    if(bigram not in ret_dict and self.freq_dict[sentence[i]] > self.threshold ):
                        ret_dict.update({bigram: len(ret_dict)})
        self.file.seek(0)
        return ret_dict
    
    def create_chars_dict(self):
        ret_dict = {}
        for sentence in self.file.readlines():
            for c in sentence:
                if(c not in ret_dict and c != '\n'):
                    ret_dict.update({c: len(ret_dict)})
        self.file.seek(0)
        return ret_dict
        

    def frequencies_dict(self):
        freq_dict = {}
        for sentence in self.file.readlines():
            for c in sentence:
                if(c not in freq_dict):
                    freq_dict.update({c: 1})
                else:
                    freq_dict.update({c: freq_dict[c]+1})

        freq_dict = {k: v for k, v in sorted(freq_dict.items(), key=lambda item: item[1])}   
        self.file.seek(0)
        return freq_dict      

    def reset(self):
        self.file.seek(0)


    
    
            
