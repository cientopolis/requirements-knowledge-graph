import spacy


class MissingParenthesis(Exception):
    """Raised when a sentence starts with parenthesis"""
    pass


class MissingNoun(Exception):
    """Raised when a word refers to a non-existing noun"""
    pass


class SentencesLoader():
    def __is_known_token(self, table, token):
        atributes = [token.dep_,          # must have same order
                     token.pos_]          # as the table

        for i in range(0, len(atributes)):
            if (atributes[i] in table[i]):
                return True
        return False

    def __is_whitelisted(self, token):
        whitelist = [["obj", "ROOT"],       # dep_
                     ["AUX"]]               # pos_

        return self.__is_known_token(whitelist, token)

    def __is_blacklisted(self, token):
        blacklist = [["cop", "advmod", "fixed"],  # dep
                     ["SCONJ", "SPACE"]]  # pos

        return self.__is_known_token(blacklist, token)

    def __keep_token(self, token):
        return ((not self.__is_blacklisted(token))
                or self.__is_whitelisted(token))

    def __add_formatting(self, sentence):
        return ('{}.'.format(' '.join(sentence).capitalize()))

    def __find_pos_(self, doc, pos_):  # can be any form of token iterable, not just a doc
        for i in range(len(doc)):
            if (doc[i].pos_ == pos_):
                return i
        return -1

    def __find_dep_(self, doc, dep_):
        for i in range(len(doc)):
            if (doc[i].dep_ == dep_):
                return i
        return -1

    def __delete_until_pos(self, doc, pos_):
        pos_ = pos_.upper()
        pos_Index = self.__find_pos_(doc, pos_)
        if (pos_Index == -1):
            return doc
        return doc[pos_Index:]

    def __trim_doc(self, doc):
        return list(filter(self.__keep_token, doc))

    def __doc_as_strings(self, doc):
        return list(map(lambda token: token.text, self.__trim_doc(doc)))

    def __get_kernel_sentence(self, doc):
        return self.__add_formatting(
            self.__doc_as_strings(
                self.__delete_until_pos(doc, "DET")))

    def __get_previous_word(self, doc):
        previous = ""
        for word in doc:
            if (word.text != '('):
                previous = word.text
            else:
                if (not previous):
                    raise MissingParenthesis()
                return previous
        raise MissingParenthesis()

    def __extract_parenthesis(self, sentence):
        return sentence[:sentence.find('(') - 1] + \
            sentence[sentence.find(')')+1:]

    def __get_sentence_from_parenthesis(self, doc):
        result = self.__get_previous_word(doc) \
            + " es " \
            + doc.text[doc.text.find('(')
                       + 1: doc.text.find(')')]

        return self.__extract_parenthesis(doc.text), result

    def __parse_parenthesis(self, doc, nlp, result):
        if (doc.text.count("(") == 0):
            return doc.text

        sentence, parsed_sentence = self.__get_sentence_from_parenthesis(doc)
        result.append(parsed_sentence)
        return self.__parse_parenthesis(nlp(sentence), nlp, result)

    def __parse_conj_y(self, doc, conjIndex):
        result = []
        verbIndex = self.__find_pos_(doc[conjIndex:], "VERB")
        if (verbIndex == -1):
            before = doc[:conjIndex]
            result.append(before.text)
            lastVerbIndex = len(before) - self.__find_pos_(
                list(reversed(before)), "AUX")      # el AUX es "varían"
            result.append(doc[:lastVerbIndex].text
                          + " "
                          + doc[conjIndex+1:].text)
        else:
            result.append(doc[:conjIndex].text)
            result.append(doc[conjIndex+1:].text)

        return result

    def __parse_conj_como(self, doc, conjIndex):
        result = []
        before = doc[:conjIndex]
        result.append(before.text)

        lastPropnIndex = len(before) \
            - self.__find_pos_(list(reversed(before)), "PROPN")
        result.append(doc[:lastPropnIndex].text
                      + " "
                      + doc[conjIndex+1:].text)
        return result

    def __parse_conjunction(self, doc):
        result = []

        conjIndex = self.__find_pos_(doc, "CCONJ")
        if (conjIndex == -1):
            result.append(doc.text)

        else:
            result += self.__parse_conj_y(doc, conjIndex)

        return result

    def __parse_double_conjunction(self, doc):
        double_conjunctions = ["como también"]
        for i in range(len(doc) - 1):
            if (doc[i].text + " " + doc[i + 1].text in double_conjunctions):
                return self.__parse_conj_como(doc, i)
        return [doc.text]

    def __has_noun(self, sentence):
        for word in sentence[:self.__find_pos_(sentence, "VERB")]:
            if (word.pos_ == "NOUN"):
                return True
        return False

    def __has_adj(self, sentence):
        for word in sentence[:self.__find_pos_(sentence, "VERB")]:
            if (word.pos_ == "ADJ"):
                return True
        return False

    def __replace_referent(self, sentences):
        result = []
        previous_noun = ""

        for st in sentences:
            if (self.__has_noun(st)):
                previous_noun = st[self.__find_pos_(st, "NOUN")].text
            elif (self.__has_adj(st)):
                previous_noun = st[self.__find_pos_(st, "ADJ")].text
            else:
                if (previous_noun):
                    sentences.remove(st)
                    explicit_st = st[:self.__find_dep_(st, "nsubj")].text \
                        + " " + previous_noun \
                        + " " + st[self.__find_dep_(st, "nsubj")+1:].text
                    result.append(explicit_st)
                else:
                    raise MissingNoun()

        sentences = list(map(lambda doc: doc.text, sentences))
        return sentences + result

    def __usable_sentences(self, paragraph):
        return [st.strip() for st in paragraph.split('.') if st]

    def __kernelize(self, sentences):
        return list(map(lambda st: self.__get_kernel_sentence(st), sentences))

    def __find_two_dep_(self, doc, dep):
        first = self.__find_dep_(doc, dep)

        if (first == -1):
            return -1, -1

        second = len(doc) - self.__find_dep_(list(reversed(doc)), dep) - 1

        if (second == first):
            return -1, -1

        return first, second

    def __is_definite_article(self, token):
        if (token.pos_ != "DET"):
            return False

        return (token.tag_[token.tag_.find("=") + 1:token.tag_.find("|")]
                == "Def")

    def __swap_object(self, doc):
        result = ""
        first, second = self.__find_two_dep_(
            doc[self.__find_pos_(doc, "VERB") + 1:],
            "obj"
        )

        if (first == -1):
            return doc.text

        first += self.__find_pos_(doc, "VERB") + 1
        second += self.__find_pos_(doc, "VERB") + 1

        if (self.__is_definite_article(doc[second - 1])):
            return doc.text

        if ((first != 0) and (doc[first - 1].pos_ == "DET")):
            # intercambiamos ambos articulos y ambos objetos
            first_pair = doc[first-1:first+1].text
            second_pair = doc[second-1:second+1].text

            return doc[:first-1].text + " " \
                + second_pair + " " \
                + doc[first+1:second-1].text + " " \
                + first_pair + " " \
                + doc[second+1:].text
        else:
            second_pair = doc[second-1:second+1].text  # cause it’s second obj

            return doc[:first].text + " " \
                + second_pair + " " \
                + doc[first+1:second-1].text + " " \
                + doc[first].text + " " \
                + doc[second+1:].text

        return doc.text


    def __simple_parse(self, sentences, nlp):
        result = []
        for st in sentences:
            sentence = self.__parse_parenthesis(nlp(st), nlp, result)
            result += self.__parse_conjunction(nlp(sentence))

        return result

    def __docerize(self, sentences, nlp):
        return list(map(lambda st: nlp(st), sentences))

    def __first_blacklist(self, doc):
        # pasar la frase que te llega por una primer blacklist
        blacklist = [["cop"],  # dep
                     []]  # pos

        result = list(map(lambda token: token.text, filter(
            lambda token: not self.__is_known_token(blacklist, token), doc)))

        return ' '.join(result).capitalize()  # acá agrega espacios de más

    def __first_filter(self, docs):
        return list(map(lambda doc: self.__first_blacklist(doc), docs))

    def parse_paragraph(self, paragraph):
        nlp = spacy.load("es")

        result = []
        sentences = self.__first_filter(
            self.__docerize(self.__usable_sentences(paragraph), nlp))

        sentences = self.__replace_referent(self.__docerize(sentences, nlp))

        for sentence in self.__simple_parse(sentences, nlp):
            result += self.__parse_double_conjunction(nlp(sentence))

        result2 = []
        for sentence in result:
            result2.append(self.__swap_object(nlp(sentence)))

        return self.__kernelize(self.__docerize(result2, nlp))
