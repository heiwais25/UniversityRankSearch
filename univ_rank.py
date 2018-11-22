import json
import string
import datrie
import marisa_trie
import time
import copy
import numpy as np

class University:
    id_cnt = 0
    def __init__(self, name, country):
        self.name = name
        self.country = country
        self.rank = {"default":-1}
        self.id = University.id_cnt
        University.id_cnt += 1

    def __repr__(self):
        return "%s, %s, %s" % (self.name, self.country, self.rank)

    def set_rank(self, rank, condition = "default"):
        self.rank[condition] = rank



class UserTrie:
    """It contains datrie library
    """
    def __init__(self):
        ALPHABET = u'abcdefghijklmnopqrstuvwxyz0123456789()&-., '
        self.trie = datrie.BaseTrie(ALPHABET)

    def insert(self, string, value):
        self.trie[string] = value

    def has_keys(self, string):
        return self.trie.has_keys_with_prefix(string)

    def get_values(self, string):
        try:
            ret = list(zip(*self.trie.items(string)))[1]
        except:
            ret = []
        return ret


class UnivRank:
    def __init__(self, src_dir = "./data/univ_rank.json"):
        """ Read DB which is created by crawling script. It contains information 
        of rank information of university in each country and subject.

        ``src_dir`` : where the src json is located in
        """
        def make_suffix_trie(sentences):
            trie = UserTrie()
            for idx, sentence in enumerate(sentences):
                sentence = sentence.lower()
                for start_idx in range(len(sentence)):
                    word = "%s%d" % (str(sentence[start_idx:]), idx)
                    trie.insert(word, idx)
            return trie

        def make_prefix_trie(sentences):
            trie = UserTrie()
            for idx, sentence in enumerate(sentences):
                sentence = sentence.lower()
                trie.insert(sentence.lower(), idx)
            return trie

        # Read University Rank
        with open(src_dir, 'r', encoding='utf-8') as fp:
            orig_univ_rank = json.load(fp)    

        # Define university class
        names = orig_univ_rank["univ_info"]["name"]
        countries = orig_univ_rank["univ_info"]["country"]
        self.indicies = orig_univ_rank["rank"]

        # Set university object with correct rank in each category
        self.univ_list = [
            University(name, country) for name, country in zip(names, countries)
            ]

        [self.univ_list[rank].set_rank(rank + 1) for rank in self.indicies["default"]]
        [self.univ_list[idx].set_rank(rank + 1, condition="country") 
            for country in self.indicies["country"] 
                for rank, idx in enumerate(self.indicies["country"][country])]
        [self.univ_list[idx].set_rank(rank + 1, condition=subject)
            for subject in self.indicies["subject"]
                for rank, idx in enumerate(self.indicies["subject"][subject])]

        # Build trie
        self.trie = {
            "univ_name" : make_suffix_trie(orig_univ_rank["univ_info"]["name"]),
            "country" : make_prefix_trie(list(self.indicies["country"].keys())),
            "subject" : make_prefix_trie(list(self.indicies["subject"].keys()))
        }

        self.category = "default"
        self.sub_category = "default"


    def set_category(self, category = "default", sub_category = "default"):
        """It will set category that we want to know rank

        ``category`` : "default", "country", "subject"
        ``sub_category`` : country name or subject name
        """
        self.category = category
        self.sub_category = sub_category

    def get_all_country(self):
        return list(self.indicies["country"].keys())

    def has_country_key(self, string):
        return string in self.indicies["country"]

    def has_subject_key(self, string):
        return string in self.indicies["subject"]

    def get_all_subject(self):
        return list(self.indicies["subject"].keys())

    def get_candidates(self, search_word="", option="univ_name", limit=50):
        if option == "univ_name":
            data_src = self.univ_list
        elif option == "country":
            data_src = list(self.indicies["country"].keys())
        else:
            data_src = list(self.indicies["subject"].keys())

        # Default option
        indicies = self.indicies[self.category]
        if self.category != "default":
            indicies = indicies[self.sub_category]

        if len(search_word) == 0:
            return copy.deepcopy([
                data_src[indicies[i]] 
                    for i in range(min(len(indicies), limit))
                    ])

        trie = self.trie[option]
        candidate_indicies = sorted(
            list(set(trie.get_values(search_word.lower())) & set(indicies))
            )
        return copy.deepcopy([
                data_src[candidate_indicies[i]] 
                    for i in range(min(len(candidate_indicies), limit))
                    ])

def main():
    start_time = time.time()
    univ_rank = UnivRank()
    print("--- %s seconds ---" %(time.time() - start_time))

    

    start_time = time.time()
    # print([univ.name for univ in univ_rank.get_candidates('timdsade')])
    print([univ.name for univ in univ_rank.get_candidates(input())])
    print([univ_rank.get_candidates('Ma', option="country")])
    print([univ_rank.get_candidates('Ma', option="subject")])

    print("--- %s seconds ---" %(time.time() - start_time))



if __name__ == "__main__":
    main()
    pass