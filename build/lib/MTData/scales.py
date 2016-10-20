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
        if self.state == 'scored':
            data = pd.pivot_table(self.dataset, index="participantDAO", columns="session")
            self.state = 'transformed'
            self.readyData = data
            self.readyData.columns = [self.__class__.__name__+'_'+'_'.join(col).strip() for col in self.readyData.columns.values]
        return self
    def __repr__(self):
        return "<Scale: name = %s, state = %s>" % (self.__class__.__name__, self.state)


class OA(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)
    def score(self):
        col_list=['anxious_freq','anxious_sev','avoid','interfere','interfere_social']
        if self.state == 'raw':
            self.dataset['SUM'] = self.dataset[col_list].mean(axis=1) * len(col_list)
            self.state = 'scored'
        return self


class DASS21_AS(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)
    def score(self):
        col_list=['breathing','dryness','heart','panic','scared','trembling','worry']
        if self.state == 'raw':
            self.dataset['SUM'] = self.dataset[col_list].mean(axis=1) * len(col_list)
            self.state = 'scored'
        return self


class DASS21_DS(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)
    def score(self):
        col_list=['blue','difficult','meaningless','hopeless','noenthusiastic','nopositive','noworth']
        if self.state == 'raw':
            self.dataset['SUM'] = self.dataset[col_list].mean(axis=1) * len(col_list)
            self.state = 'scored'
        return self

class QOL(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)
    def score(self):
        col_list=['children', 'expression', 'friend', 'health', 'helping',  'independence', 'learning', 'material', 'reading', 'recreation', 'relationships', 'socializing', 'spouse', 'understanding', 'work']
        if self.state == 'raw':
            self.dataset['SUM'] = self.dataset[col_list].mean(axis=1) * len(col_list)
            self.state = 'scored'
        return self

class RR(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)
    def score(self):
        target_list= [itemname for itemname in list(self.dataset.columns.values) if itemname.endswith('_NS')]
        nonTarget_list= [itemname for itemname in list(self.dataset.columns.values) if itemname.endswith(tuple(['_NF','_PF','_PS']))]
        positive_list= [itemname for itemname in list(self.dataset.columns.values) if itemname.endswith('_PS')]
        if self.state == 'raw':
            self.dataset['Score'] = self.dataset[target_list].mean(axis=1) / self.dataset[nonTarget_list].mean(axis=1)
            self.dataset['Negative_Ave'] = self.dataset[target_list].mean(axis=1)
            self.dataset['Positive_Ave'] = self.dataset[positive_list].mean(axis=1)
            self.state = 'scored'
        return self

class BBSIQ(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)
    def score(self):
        physical_list=['breath_suffocate', 'chest_heart', 'confused_outofmind', 'dizzy_ill', 'heart_wrong', 'lightheaded_faint', 'vision_illness']
        nonPhysical_list=['breath_flu', 'breath_physically', 'vision_glasses', 'vision_strained', 'lightheaded_eat', 'lightheaded_sleep', 'chest_indigestion', 'chest_sore', 'heart_active', 'heart_excited', 'confused_cold', 'confused_work', 'dizzy_ate', 'dizzy_overtired']
        threat_list=['visitors_bored', 'shop_irritating', 'smoke_house', 'friend_incompetent', 'jolt_burglar', 'party_boring', 'urgent_died']
        nonThreat_list=['visitors_engagement', 'visitors_outstay', 'shop_bored', 'shop_concentrating', 'smoke_cig', 'smoke_food', 'friend_helpful', 'friend_moreoften', 'jolt_dream', 'jolt_wind', 'party_hear', 'party_preoccupied','urgent_bill', 'urgent_junk']
        if self.state == 'raw':
            self.dataset['Physical_Score'] = self.dataset[physical_list].mean(axis=1) / self.dataset[nonPhysical_list].mean(axis=1)
            self.dataset['External_Threat_Score'] = self.dataset[threat_list].mean(axis=1) / self.dataset[nonThreat_list].mean(axis=1)
            self.dataset['Negative_Ave'] = self.dataset[physical_list + threat_list].mean(axis=1)
            self.dataset['Other_Ave'] = self.dataset[nonPhysical_list + nonThreat_list].mean(axis=1)
            self.state = 'scored'
        return self

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
