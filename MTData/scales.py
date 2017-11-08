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
        self.state = state; # use the function alone, state=False, use the function based on other functions state=True
        self.isscore=False; # if the class has score function or not
        self.lname=[i for i in self.dataset.columns.values if i not in ['id', 'date','participantRSA','session','tag','timeOnPage']]
        # variable list
    def score(self):
        raise NotImplementedError("Subclass must implement abstract method")
    def trans(self):
        if self.state and self.isscore:
            # transform the scored form
            wide = pd.pivot_table(self.score(), index="participantRSA", columns="session")
            wide.columns = [self.__class__.__name__+'_'+'_'.join(col).strip() for col in wide.columns.values];
        else:
            # transform the original dataset.
            wide = pd.pivot_table(self.dataset, index="participantRSA", columns="session")
            wide.columns = [self.__class__.__name__+'_'+'_'.join(col).strip() for col in wide.columns.values];
        return wide

    def __repr__(self):
        return "<Scale: name = %s, state = %s>" % (self.__class__.__name__, self.state)
    def alo(self):
        print 'Scale_aloha'
        # report the number of missing data
    def miss_DATA(self):
        # check missing data
        if 'tag' in self.dataset.columns.values:
            return self.dataset.drop('tag', 1).isnull().sum();
        else:
            return self.dataset.isnull().sum();

    def pnum(self):
        # report the number of paricipants
        for sname in self.dataset.columns.values:
            if 'participant' in sname:
                p_key=sname;
        return self.dataset[p_key].unique().size

    def isdup(self):
        # report how many duplicated entries
        return len(self.dataset.axes[0])-len(self.drop_dup().axes[0])

    def drop_dup(self):
        # drop duplicated data
        for sname in self.dataset.columns.values:
            if 'participant' in sname:
                p_key=sname;
        if 'session' in self.dataset.columns.values:
            #print "session exits"
            if 'tag' in self.dataset.columns.values:
                if 'sessionId' in self.dataset.columns.values:
                    return self.dataset.drop_duplicates([p_key,'session','tag','sessionId'], keep='last', inplace=False)
                else:
                #print 'tag exits'
                    return self.dataset.drop_duplicates([p_key,'session','tag'], keep='last', inplace=False)
            #print 'tag doesnt exits'
            elif 'trial_index' in self.dataset.columns.values:
                return self.dataset.drop_duplicates([p_key,'session','trial_index'], keep='last', inplace=False)
            else:
                return self.dataset.drop_duplicates([p_key,'session'], keep='last', inplace=False)
        else:
            #print "session and tag doesn't exits"
            return self.dataset.drop_duplicates([p_key], keep='last', inplace=False)
    def data_range(self):
        #default data range fucntion report all true
        return [True]*len(self.lname);




class OA(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)
        self.lname=['anxious_freq','anxious_sev','avoid','interfere','interfere_social'];
        self.isscore=True
        #self.srange=list(range(0,5)).append(555);

    def score(self):
        #self.scoring = True
        #col_list=['anxious_freq','anxious_sev','avoid','interfere','interfere_social']
        if self.state:
            scores=self.drop_dup()[['participantRSA','session']].copy()
            scores['SUM']= self.drop_dup()[self.lname].mean(axis=1) * len(self.lname)
        else:
            scores=self.dataset[['participantRSA','session']].copy()
            scores['SUM']= self.dataset[self.lname].mean(axis=1) * len(self.lname)
        return scores
        # report if data of every variable is within the data_range
    def data_range(self):
        #lname=['anxious_freq','anxious_sev','avoid','interfere','interfere_social']
        af_range=[];
        af_std=range(0,5);
        af_std.append(555);
        for sname in self.lname:
            ss_af=set(filter(lambda x: x == x , set(self.dataset[sname].unique())));
            af_range.append(ss_af<=set(af_std));

        return af_range;



class DASS21_AS(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)
        self.lname=['breathing','dryness','heart','panic','scared','trembling','worry']
        self.isscore=True
    def score(self):
        if self.state:
            scores=self.drop_dup()[['participantRSA','session']].copy()
            scores['SUM']= self.drop_dup()[self.lname].mean(axis=1) * len(self.lname)
        else:
            scores=self.dataset[['participantRSA','session']].copy()
            scores['SUM']= self.dataset[self.lname].mean(axis=1) * len(self.lname)
        return scores
    def data_range(self):
        #lname=['anxious_freq','anxious_sev','avoid','interfere','interfere_social']
        af_range=[];
        af_std=range(0,4);
        af_std.append(-1);
        for sname in self.lname:
            ss_af=set(filter(lambda x: x == x , set(self.dataset[sname].unique())));
            af_range.append(ss_af<=set(af_std));
        return af_range;


class DASS21_DS(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)
        #self.lname=[i for i in self.dataset.columns.values if i not in ['id', 'date','participantRSA','session']]
        self.isscore=True
    def score(self):
        #col_list=['anxious_freq','anxious_sev','avoid','interfere','interfere_social']
        if self.state:
            scores=self.drop_dup()[['participantRSA','session']].copy()
            scores['SUM']= self.drop_dup()[self.lname].mean(axis=1) * len(self.lname)
        else:
            scores=self.dataset[['participantRSA','session']].copy()
            scores['SUM']= self.dataset[self.lname].mean(axis=1) * len(self.lname)
        return scores
    def data_range(self):
        #lname=['anxious_freq','anxious_sev','avoid','interfere','interfere_social']
        af_range=[];
        af_std=range(0,4);
        af_std.append(-1);
        for sname in self.lname:
            ss_af=set(filter(lambda x: x == x , set(self.dataset[sname].unique())));
            af_range.append(ss_af<=set(af_std));
        return af_range;

class QOL(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)
        #self.lname=[i for i in self.dataset.columns.values if i not in ['id', 'date','participantRSA','session']]
        self.isscore=True
    def score(self):
        #col_list=['anxious_freq','anxious_sev','avoid','interfere','interfere_social']
        if self.state:
            scores=self.drop_dup()[['participantRSA','session']].copy()
            scores['SUM']= self.drop_dup()[self.lname].mean(axis=1) * len(self.lname)
        else:
            scores=self.dataset[['participantRSA','session']].copy()
            scores['SUM']= self.dataset[self.lname].mean(axis=1) * len(self.lname)
        return scores
    def data_range(self):
        #lname=[i for i in self.dataset.columns.values if i not in ['id', 'date','participantRSA','session']]
        af_range=[];
        af_std=range(1,6);
        af_std.append(555);
        for sname in self.lname:
            ss_af=set(filter(lambda x: x == x , set(self.dataset[sname].unique())));
            af_range.append(ss_af<=set(af_std));
        return af_range;

class RR(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)
        #self.lname=[i for i in self.dataset.columns.values if i not in ['id', 'date','participantRSA','session']]
        self.isscore=True
    def score(self):
        target_list= [itemname for itemname in list(self.dataset.columns.values) if itemname.endswith('_NS')]
        nonTarget_list= [itemname for itemname in list(self.dataset.columns.values) if itemname.endswith(tuple(['_NF','_PF','_PS']))]
        positive_list= [itemname for itemname in list(self.dataset.columns.values) if itemname.endswith('_PS')]
        if self.state:
            scores=self.drop_dup()[['participantRSA','session']].copy()
            scores['Score'] = self.drop_dup()[target_list].mean(axis=1) / self.dataset[nonTarget_list].mean(axis=1)
            scores['Negative_Ave'] = self.drop_dup()[target_list].mean(axis=1)
            scores['Positive_Ave'] = self.drop_dup()[positive_list].mean(axis=1)

        else:
            scores=self.dataset[['participantRSA','session']].copy()
            scores['Score'] = self.dataset[target_list].mean(axis=1) / self.dataset[nonTarget_list].mean(axis=1)
            scores['Negative_Ave'] = self.dataset[target_list].mean(axis=1)
            scores['Positive_Ave'] = self.dataset[positive_list].mean(axis=1)

        return scores
    def data_range(self):
        #lname=[i for i in self.dataset.columns.values if i not in ['id', 'date','participantRSA','session']]
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
        self.isscore=True
    def score(self):
        physical_list=['breath_suffocate', 'chest_heart', 'confused_outofmind', 'dizzy_ill', 'heart_wrong', 'lightheaded_faint', 'vision_illness']
        nonPhysical_list=['breath_flu', 'breath_physically', 'vision_glasses', 'vision_strained', 'lightheaded_eat', 'lightheaded_sleep', 'chest_indigestion', 'chest_sore', 'heart_active', 'heart_excited', 'confused_cold', 'confused_work', 'dizzy_ate', 'dizzy_overtired']
        threat_list=['visitors_bored', 'shop_irritating', 'smoke_house', 'friend_incompetent', 'jolt_burglar', 'party_boring', 'urgent_died']
        nonThreat_list=['visitors_engagement', 'visitors_outstay', 'shop_bored', 'shop_concentrating', 'smoke_cig', 'smoke_food', 'friend_helpful', 'friend_moreoften', 'jolt_dream', 'jolt_wind', 'party_hear', 'party_preoccupied','urgent_bill', 'urgent_junk']
        if self.state:
            scores=self.drop_dup()[['participantRSA','session']].copy()
            scores['Physical_Score'] = self.drop_dup()[physical_list].mean(axis=1) / self.dataset[nonPhysical_list].mean(axis=1)
            scores['External_Threat_Score'] = self.drop_dup()[threat_list].mean(axis=1) / self.dataset[nonThreat_list].mean(axis=1)
            scores['Negative_Ave'] = self.drop_dup()[physical_list + threat_list].mean(axis=1)
            scores['Other_Ave'] = self.drop_dup()[nonPhysical_list + nonThreat_list].mean(axis=1)

        else:
            scores=self.dataset[['participantRSA','session']].copy()
            scores['Physical_Score'] = self.dataset[physical_list].mean(axis=1) / self.dataset[nonPhysical_list].mean(axis=1)
            scores['External_Threat_Score'] = self.dataset[threat_list].mean(axis=1) / self.dataset[nonThreat_list].mean(axis=1)
            scores['Negative_Ave'] = self.dataset[physical_list + threat_list].mean(axis=1)
            scores['Other_Ave'] = self.dataset[nonPhysical_list + nonThreat_list].mean(axis=1)

        return scores
    def data_range(self):
        #lname=['anxious_freq','anxious_sev','avoid','interfere','interfere_social']
        af_range=[];
        af_std=range(0,5);
        af_std.append(555);
        for sname in self.lname:
            ss_af=set(filter(lambda x: x == x , set(self.dataset[sname].unique())));
            af_range.append(ss_af<=set(af_std));
        return af_range;



class CC(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)
    def data_range(self):
        #lname=['anxious_freq','anxious_sev','avoid','interfere','interfere_social']
        af_range=[];
        af_std=range(1,6);
        #af_std.append(555);
        for sname in self.lname:
            ss_af=set(filter(lambda x: x == x , set(self.dataset[sname].unique())));
            af_range.append(ss_af<=set(af_std));
        return af_range;
class MH(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)




class MentalHealthHistory(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)
    def miss_DATA(self):
        # check missing data
        return self.dataset.drop(['other_Desc', 'other_DescNo', 'other_HelpChange', 'other_HelpCurrent', 'other_HelpPast','other_NoHelpReason','tag'], 1).isnull().sum();
    def data_range(self):
        data_list=['app', 'app_past', 'book', 'book_past', 'coach', 'coach_past', 'family', 'family_past', 'friend', 'friend_past', 'general_practitioner', 'general_practitioner_past', 'lmhc', 'lmhc_past', 'medicine', 'medicine_past', 'online', 'online_past', 'other',
        'other_past', 'psychiatrist', 'psychiatrist_past', 'psychologist', 'psychologist_past', 'religious_leader', 'religious_leader_past', 'school_counselor', 'school_counselor_past', 'support_group', 'support_group_past', 'teacher', 'teacher_past']

        mul_choice_list=['changeHelp' 'disorders' 'help' 'noHelp_Reason' 'pastDisorders' 'pastHelp'];

        Desc_list=['other_Desc', 'other_DescNo', 'other_HelpChange', 'other_HelpCurrent', 'other_HelpPast','other_NoHelpReason'];
        af_range=[];
        af_std=range(0,9);
        af_std.append(555);
        for sname in self.lname:
            ss_af=set(filter(lambda x: x == x , set(self.dataset[sname].unique())));
            if sname in data_list:
                af_range.append(ss_af<=set(af_std));
            elif sname in mul_choice_list:
                Cho_list=[];
                Desc_list=[];
                for anychoice in ss_af:
                    Cho_list.append(isinstance(eval(anychoice), list));
                    if all(Cho_list):
                        af_range.append(True)
                    else:
                        af_range.append(False)

            else:
                for anydesc in ss_af:
                    Desc_list.append(isinstance(anydesc, basestring));
                    if all(Desc_list):
                        af_range.append(True)
                    else:
                        af_range.append(False)

        return af_range;




class WhatIBelieve(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)
    def data_range(self):

        af_range=[];
        af_std=range(0,5);
        af_std.append(555);
        for sname in self.lname:
            ss_af=set(filter(lambda x: x == x , set(self.dataset[sname].unique())));
            af_range.append(ss_af<=set(af_std));
        return af_range;

class JsPsychTrial(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)


class Credibility(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)
    def data_range(self):

        af_range=[];
        af_std=range(0,5);
        #af_std.append(555);
        for sname in self.lname:
            ss_af=set(filter(lambda x: x == x , set(self.dataset[sname].unique())));
            af_range.append(ss_af<=set(af_std));
        return af_range;

class Demographic(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)


class Demographics(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)

class Relatability(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)
    def data_range(self):

        af_range=[];
        af_std=range(1,6);
        af_std.append(555);
        for sname in self.lname:
            ss_af=set(filter(lambda x: x == x , set(self.dataset[sname].unique())));
            af_range.append(ss_af<=set(af_std));
        return af_range;
class Affect(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state);
        #self.lname=["negFeelings","posFeelings"]
    def data_range(self):
        af_range=[];
        af_std=range(0,21);
        af_std.append(555);
        for sname in self.lname:
            ss_af=set(filter(lambda x: x == x , set(self.dataset[sname].unique())));
            af_range.append(ss_af<=set(af_std));
        return af_range;

class AxImagery(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state);
        self.lname=["negFeelings","posFeelings"]
    def data_range(self):
        af_range=[];
        af_std=range(0,21);
        af_std.append(555);
        for sname in self.lname:
            ss_af=set(filter(lambda x: x == x , set(self.dataset[sname].unique())));
            af_range.append(ss_af<=set(af_std));
        return af_range;

class HelpSeeking(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state);
        #self.lname=[i for i in self.dataset.columns.values if i not in ['id', 'date','participantRSA','session','tag','timeOnPage']]
        #self.otherDesc=['other'];
    def miss_DATA(self):
        # check missing data
        return self.dataset.drop(['tag','other'], 1).isnull().sum();

    def data_range(self):
        af_range=[];
        af_std=[True,False];
        #af_std.append(555);
        for sname in self.lname:
            ss_af=set(filter(lambda x: x == x , set(self.dataset[sname].unique())));
            if sname == 'changeInHelp_noAns':
                af_range.append(ss_af<=set([0,555]));
            elif sname == 'other':
                other_list=[];
                for otherReason in ss_af:
                    other_list.append(isinstance(otherReason, basestring));
                if all(other_list):
                    af_range.append(True)
                else:
                    af_range.append(False)
            else:
                af_range.append(ss_af<=set(af_std));
        return af_range;

class Phq4(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)
    def data_range(self):

        af_range=[];
        af_std=range(0,4);
        #af_std.append(5);
        for sname in self.lname:
            ss_af=set(filter(lambda x: x == x , set(self.dataset[sname].unique())));
            af_range.append(ss_af<=set(af_std));
        return af_range;

class Evaluation(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)
    def data_range(self):
        tf_li=['commute','home','noAns_Distracted','noAns_Easy','noAns_Helpful','noAns_Interest','noAns_Like','noAns_Looks','noAns_Mood','noAns_OtherTreatment','noAns_Privacy','noAns_Problems','noAns_Quality','noAns_Recommend','noAns_Similar','noAns_Tiring','noAns_TrustInfo','noAns_UnderstandAssessment','oAns_UnderstandTraining','otherComplete','otherTreatment','public','vacation','work']
        int_li=['condition','distracted','easy','helpful','idealSessions','interest','likeGral','likedLooks','problem','quality','recommend','similar','tiring','trustInfo','understandAssessment','understandTraining'];

        af_range=[];
        af_std=range(0,5);
        #af_std.append(5);
        for sname in self.lname:
            ss_af=set(filter(lambda x: x == x , set(self.dataset[sname].unique())));
            if sname in int_li:
                af_range.append(ss_af<=set(af_std));
            else:
                af_range.append(ss_af<=set([True,False]));
        return af_range;

class SUDS(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)
    def data_range(self):
        af_range=[];
        af_std=range(0,101);
        #af_std.append(555);
        for sname in self.lname:
            ss_af=set(filter(lambda x: x == x , set(self.dataset[sname].unique())));
            af_range.append(ss_af<=set(af_std));
        return af_range;
class ExpectancyBias(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)
        self.lname=[i for i in self.dataset.columns.values if i not in ['id', 'date','participant','session','sessionId','tag']];
    def miss_DATA(self):
        # check missing data
        f5=self.dataset;

        return f5.dropna(subset = ['participant', 'session']).drop(['tag','sessionId'], 1).isnull().sum();

    def data_range(self):

        af_range=[];
        af_std=range(1,8);
        af_std.append(555);
        for sname in self.lname:
            ss_af=set(filter(lambda x: x == x , set(self.dataset[sname].unique())));
            af_range.append(ss_af<=set(af_std));
        return af_range;

class ImageryPrime(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)


class ImpactAnxiousImagery(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)
    def data_range(self):
        af_range=[];
        af_std=range(1,6);
        af_std.append(-1);
        for sname in self.lname:
            ss_af=set(filter(lambda x: x == x , set(self.dataset[sname].unique())));
            if sname =="anxiety":
                af_range.append(ss_af<=set(range(0,101)));
            else:
                af_range.append(ss_af<=set(af_std));
        return af_range;

class AnxietyTriggers(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)
        self.lname.remove('howLong');
    def data_range(self):
        af_range=[];
        af_std=range(1,6);
        af_std.append(555);
        for sname in self.lname:
            ss_af=set(filter(lambda x: x == x , set(self.dataset[sname].unique())));

            af_range.append(ss_af<=set(af_std));
        return af_range;

class DD(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)
    def data_range(self):
        af_range=[];
        af_std=range(0,101);
        bf_std=range(0,26);
        cf_std=range(0,12)
        bf_std.append(555);
        af_std.append(555);
        for sname in self.lname:
            ss_af=set(filter(lambda x: x == x , set(self.dataset[sname].unique())));
            if sname in ['q1_noAns','q2_noAns']:
                #ss_af=set(filter(lambda x: x == x , set(self.dataset[sname].unique())));
                af_range.append(ss_af<=set([True,False]));
            elif sname =='average_amount':
                af_range.append(ss_af<=set(bf_std));
            elif sname =='average_freq':
                af_range.append(ss_af<=set(af_std));
            else:
                af_range.append(ss_af<=set(af_std));
        return af_range;

class DD_FU(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)

    def data_range(self):
        af_range=[];
        af_std=range(0,101);
        bf_std=range(0,26);
        cf_std=range(0,12)
        bf_std.append(555);
        af_std.append(555);
        for sname in self.lname:
            ss_af=set(filter(lambda x: x == x , set(self.dataset[sname].unique())));
            if sname in ['q1_noAns','q2_noAns']:
                #ss_af=set(filter(lambda x: x == x , set(self.dataset[sname].unique())));
                af_range.append(ss_af<=set([True,False]));
            elif sname =='average_amount':
                af_range.append(ss_af<=set(bf_std));
            elif sname =='average_freq':
                af_range.append(ss_af<=set(af_std));
            else:
                af_range.append(ss_af<=set(af_std));
        return af_range;

class MentalHealthHxTx(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)

    def data_range(self):
        data_list=['book','book_past','coach','coach_past','family','famliy_past','friend','friend_past','general_practitioner','general_practitioner_past','imhc','imhc_past','medicine','medicine_past','online','online_past','other','other_past','psychiatrist','psychiatrist_past','psychologist','psychologist_past',
        'religious_leader','religious_leader_past',	'school_counselor',	'school_counselor_past','session','teacher','teacher_past']
        mul_choice_list=['disorders','disorders_past','help','help_past','noHelp_Reason'];
        Desc_list=['otherDesc','otherDescNo','otherHelpCurrent','otherHelpPast','otherReason'];
        self.otherDesc=Desc_list;


        af_range=[];
        af_std=range(1,8);
        af_std.append(555);
        for sname in self.lname:
            ss_af=set(filter(lambda x: x == x , set(self.dataset[sname].unique())));
            if sname in data_list:

                af_range.append(ss_af<=set(af_std));
            elif sname in mul_choice_list:
                Cho_list=[];
                Desc_list=[];
                for anychoice in ss_af:
                    Cho_list.append(isinstance(anychoice, list));
                if all(Cho_list):
                    af_range.append(True)
                else:
                    af_range.append(False)

            else:
                for anydesc in ss_af:
                    Desc_list.append(isinstance(anydesc, basestring));
                if all(Desc_list):
                    af_range.append(True)
                else:
                    af_range.append(False)

        return af_range;

class JsPsychTrial(Scale):
    def __init__(self,dataset,state):
        Scale.__init__(self,dataset,state)
    def miss_DATA(self):
        # check missing data

        return self.dataset.drop(['button_pressed'], 1).isnull().sum();
