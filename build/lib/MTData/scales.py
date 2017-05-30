# meta class for scales
# Scales should have three component:
# 1\ name = name of the scale
# 2\ state = raw, scored, transformed
# 3\ dataset = the original dataset of the scale
# 4\ score function = if the target dataset is raw, scored it and return another scale object.
# 5\ trans function = if the target dataset is scored, transform it and return another scale object.
import pandas as pd
class Scale:
    def __init__(self,dataset,state):
        self.dataset = dataset.drop('id', 1).drop_duplicates()
        self.state = state

    def score(self):
        raise NotImplementedError("Subclass must implement abstract method")
    def trans(self):
        wide = pd.pivot_table(self.score(), index="participantRSA", columns="session")
            #self.readyData = data
            #self.readyData.columns
        wide.columns = [self.__class__.__name__+'_'+'_'.join(col).strip() for col in wide.columns.values]
        return wide

    def __repr__(self):
        return "<Scale: name = %s, state = %s>" % (self.__class__.__name__, self.state)
    def alo(self):
        print 'Scale_aloha'
        # report the number of missing data
    def miss_DATA(self):
        return self.dataset.isnull().sum()
        # report the number of paricipants
    def pnum(self):
        return self.dataset['participantRSA'].unique().size

    def isdup(self):
        return len(self.dataset.axes[0])-len(self.drop_dup().axes[0])

    def drop_dup(self):
        if 'session' in self.dataset.columns.values:
            #print "session exits"
            if 'tag' in self.dataset.columns.values:
                #print 'tag exits'
                return self.dataset.drop_duplicates(['participantRSA','session','tag'], keep='last', inplace=False)
            #print 'tag doesnt exits'
            return self.dataset.drop_duplicates(['participantRSA','session'], keep='last', inplace=False)
        else:
            #print "session and tag doesn't exits"
            return self.dataset.drop_duplicates(['participantRSA'], keep='last', inplace=False)





class OA(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)
        self.lname=['anxious_freq','anxious_sev','avoid','interfere','interfere_social'];
        #self.srange=list(range(0,5)).append(555);

    def score(self):
        #col_list=['anxious_freq','anxious_sev','avoid','interfere','interfere_social']
        if self.state == 'raw':
            scores=self.drop_dup()[['participantRSA','session']].copy()
            scores['SUM']= self.drop_dup()[self.lname].mean(axis=1) * len(self.lname)
            self.state = 'scored'
        return scores
        # report if data of every variable is within the data_range
    def data_range(self):
        #lname=['anxious_freq','anxious_sev','avoid','interfere','interfere_social']
        af_range=[];
        af_std=range(0,5);
        af_std.append(555);
        for sname in self.lname:
            af_range.append(set(self.dataset[sname].unique())<=set(af_std));

        return af_range;



class DASS21_AS(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)
        self.lname=[i for i in self.dataset.columns.values if i not in ['id', 'date','participantRSA','session']]
    def score(self):
        #col_list=['anxious_freq','anxious_sev','avoid','interfere','interfere_social']
        if self.state == 'raw':
            scores=self.dataset[['participantRSA','session']].copy()
            scores['SUM']= self.dataset[self.lname].mean(axis=1) * len(self.lname) * 2
            self.state = 'scored'
        return scores
    def data_range(self):
        #lname=['anxious_freq','anxious_sev','avoid','interfere','interfere_social']
        af_range=[];
        af_std=range(0,4);
        af_std.append(-1);
        for sname in self.lname:
            af_range.append(set(self.dataset[sname].unique())<=set(af_std));
        return af_range;


class DASS21_DS(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)
        self.lname=[i for i in self.dataset.columns.values if i not in ['id', 'date','participantRSA','session']]
    def score(self):
        #col_list=['anxious_freq','anxious_sev','avoid','interfere','interfere_social']
        if self.state == 'raw':
            scores=self.dataset[['participantRSA','session']].copy()
            scores['SUM']= self.dataset[self.lname].mean(axis=1) * len(self.lname) * 2
            self.state = 'scored'
        return scores
    def data_range(self):
        #lname=['anxious_freq','anxious_sev','avoid','interfere','interfere_social']
        af_range=[];
        af_std=range(0,4);
        af_std.append(-1);
        for sname in self.lname:
            af_range.append(set(self.dataset[sname].unique())<=set(af_std));
        return af_range;

class QOL(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)
    def score(self):
        #col_list=['anxious_freq','anxious_sev','avoid','interfere','interfere_social']
        if self.state == 'raw':
            scores=self.dataset[['participantRSA','session']].copy()
            scores['SUM']= self.dataset[self.lname].mean(axis=1) * len(self.lname)
            self.state = 'scored'
        return scores


class RR(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)
        self.lname=[i for i in self.dataset.columns.values if i not in ['id', 'date','participantRSA','session']]
    def score(self):
        target_list= [itemname for itemname in list(self.dataset.columns.values) if itemname.endswith('_NS')]
        nonTarget_list= [itemname for itemname in list(self.dataset.columns.values) if itemname.endswith(tuple(['_NF','_PF','_PS']))]
        positive_list= [itemname for itemname in list(self.dataset.columns.values) if itemname.endswith('_PS')]
        if self.state == 'raw':
            scores=self.dataset[['participantRSA','session']].copy()
            scores['Score'] = self.dataset[target_list].mean(axis=1) / self.dataset[nonTarget_list].mean(axis=1)
            scores['Negative_Ave'] = self.dataset[target_list].mean(axis=1)
            scores['Positive_Ave'] = self.dataset[positive_list].mean(axis=1)
            self.state = 'scored'
        return scores
    def data_range(self):
        lname=[i for i in self.dataset.columns.values if i not in ['id', 'date','participantRSA','session']]
        af_range=[];
        af_std=range(0,4);
        af_std.append(-1);
        for sname in self.lname:
            ss_af=set(filter(lambda x: x == x , set(self.dataset[sname].unique())));
            af_range.append(ss_af<=set(af_std));
        return af_range;


class BBSIQ(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)
        self.lname=[i for i in self.dataset.columns.values if i not in ['id', 'date','participantRSA','session']]
    def score(self):
        physical_list=['breath_suffocate', 'chest_heart', 'confused_outofmind', 'dizzy_ill', 'heart_wrong', 'lightheaded_faint', 'vision_illness']
        nonPhysical_list=['breath_flu', 'breath_physically', 'vision_glasses', 'vision_strained', 'lightheaded_eat', 'lightheaded_sleep', 'chest_indigestion', 'chest_sore', 'heart_active', 'heart_excited', 'confused_cold', 'confused_work', 'dizzy_ate', 'dizzy_overtired']
        threat_list=['visitors_bored', 'shop_irritating', 'smoke_house', 'friend_incompetent', 'jolt_burglar', 'party_boring', 'urgent_died']
        nonThreat_list=['visitors_engagement', 'visitors_outstay', 'shop_bored', 'shop_concentrating', 'smoke_cig', 'smoke_food', 'friend_helpful', 'friend_moreoften', 'jolt_dream', 'jolt_wind', 'party_hear', 'party_preoccupied','urgent_bill', 'urgent_junk']
        if self.state == 'raw':
            scores=self.dataset[['participantRSA','session']].copy()
            scores['Physical_Score'] = self.dataset[physical_list].mean(axis=1) / self.dataset[nonPhysical_list].mean(axis=1)
            scores['External_Threat_Score'] = self.dataset[threat_list].mean(axis=1) / self.dataset[nonThreat_list].mean(axis=1)
            scores['Negative_Ave'] = self.dataset[physical_list + threat_list].mean(axis=1)
            scores['Other_Ave'] = self.dataset[nonPhysical_list + nonThreat_list].mean(axis=1)
            self.state = 'scored'
        return scores
    def data_range(self):
        #lname=['anxious_freq','anxious_sev','avoid','interfere','interfere_social']
        af_range=[];
        af_std=range(0,5);
        af_std.append(555);
        for sname in self.lname:
            af_range.append(set(self.dataset[sname].unique())<=set(af_std));
        return af_range;


class CC(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)

class MH(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)

class SUDS(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)

class ImpactAnxiousImagery(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)
