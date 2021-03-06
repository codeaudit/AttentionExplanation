from common import *

class DataHolder() :
    def __init__(self, **kwargs) :
        self.attributes = []
        for n, v in kwargs.items() :
            setattr(self, n, v)
            self.attributes.append(n)

    def get_stats(self, field) :
        assert field in self.attributes
        lens = [len(x) - 2 for x in getattr(self, field)]
        return {
            'min_length' : min(lens),
            'max_length' : max(lens),
            'mean_length' : np.mean(lens),
            'std_length' : np.std(lens)
        }

def getFromDict(dataDict, maplist):
    first, rest = maplist[0], maplist[1:]
    if rest: return getFromDict(dataDict[first], rest)
    else: return dataDict[first]

def get_data_from_vec(vec, _types, sort=False) :
    get = lambda x : getFromDict(x, _types)
    P, Q, E, A = get(vec.paragraphs), get(vec.questions), get(vec.entity_masks), get(vec.answers)
    if sort :
        sorting_idx = np.argsort([len(x) for x in P])
        sort = lambda l : permute_list(l, sorting_idx)
        
        P, Q, E, A = sort(P), sort(Q), sort(E), sort(A)
        
    data = DataHolder(P=P, Q=Q, E=E, A=A)
    return data

class Dataset() :
    def __init__(self, name, path=None, vec=None, filters=[]) :
        self.name = name
        self.vec = pickle.load(open(path, 'rb')) if vec is None else vec
        self.vec.entity_size = len(self.vec.entity2idx)

        self.train_data = get_data_from_vec(self.vec, ['train'] + filters)
        self.test_data = get_data_from_vec(self.vec, ['test'] + filters, sort=True)
        self.by_class = False

    def display_stats(self) :
        stats = {}
        stats['vocab_size'] = self.vec.vocab_size
        stats['embed_size'] = self.vec.word_dim
        stats['hidden_size'] = self.vec.hidden_size

        if self.by_class :
            y = np.unique(np.array(self.train_data.A), return_counts=True)
            yt = np.unique(np.array(self.test_data.A), return_counts=True)

            stats['train_size'] = list(zip(y[0].tolist(), y[1].tolist()))
            stats['test_size'] = list(zip(yt[0].tolist(), yt[1].tolist()))
        else :
            stats['train_size'] = [("Overall", len(self.train_data.A))]
            stats['test_size'] = [("Overall", len(self.test_data.A))]

        outdir = "datastats"
        os.makedirs('graph_outputs/' + outdir, exist_ok=True)
        stats.update(self.train_data.get_stats('P'))

        json.dump(stats, open('graph_outputs/' + outdir + '/' + self.name + '.txt', 'w'))
        print(stats)

def get_SNLI() :
    SNLI_dataset = Dataset(name='snli', path='preprocess/SNLI/vec_snli.p')
    SNLI_dataset.by_class = True
    return SNLI_dataset

def get_CNN() :
    CNN_dataset = Dataset(name='cnn', path='preprocess/CNN/vec_cnn.p')
    return CNN_dataset

def get_Babi_1() :
    Babi_1_dataset = Dataset(name='babi_1', path='preprocess/Babi/babi.p', filters=['qa1_single-supporting-fact_'])
    Babi_1_dataset.vec.word_dim = 50
    return Babi_1_dataset

def get_Babi_2() :
    Babi_2_dataset = Dataset(name='babi_2', path='preprocess/Babi/babi.p', filters=['qa2_two-supporting-facts_'])
    Babi_2_dataset.vec.word_dim = 50
    return Babi_2_dataset

def get_Babi_3() :
    Babi_3_dataset = Dataset(name='babi_3', path='preprocess/Babi/babi.p', filters=['qa3_three-supporting-facts_'])
    Babi_3_dataset.vec.word_dim = 50
    return Babi_3_dataset

datasets = {
    'snli' : get_SNLI, 
    'cnn' : get_CNN, 
    'babi_1' : get_Babi_1, 
    'babi_2' : get_Babi_2, 
    'babi_3' : get_Babi_3
}