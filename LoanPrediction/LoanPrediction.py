# -*- coding: utf-8 -*-
"""
Created on Wed Jun 22 20:01:40 2016

@author: Pablo

zdroj: http://www.analyticsvidhya.com/blog/2016/01/complete-tutorial-learn-data-science-python-scratch-2/


"""

import pandas as pd
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt

from sklearn.preprocessing import LabelEncoder
from sklearn.cross_validation import KFold   #For K-fold cross validation
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier, export_graphviz
from sklearn import metrics

from sklearn.cross_validation import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix

from sklearn.svm import SVC
from sklearn.preprocessing import scale
from sklearn.ensemble import GradientBoostingClassifier
from sklearn import cross_validation, metrics


from matplotlib.colors import ListedColormap
cmap_light = ListedColormap(['#FFAAAA', '#AAFFAA', '#AAAAFF'])
cmap_bold = ListedColormap(['#FF0000', '#00FF00', '#0000FF'])
cm = plt.cm.RdBu
cm_bright = ListedColormap(['#FF0000', '#0000FF'])




'''
- split na train a test set
- gridsearch
- vysledok je best estimator a vypise best skore
'''
def cv_optimize(clf, parameters, Xtrain, ytrain, n_folds=5):
    gs = GridSearchCV(clf, param_grid=parameters, cv=n_folds)
    gs.fit(Xtrain, ytrain)
    print ("BEST PARAMS", gs.best_params_)
    best = gs.best_estimator_
    return best




'''
Funkcia na tunovanie parametrov. Data sa delia. na trainsete sa robi 5 fold CV.
Najlepsi parameter je potom pouzity na celom training sete.
Vypise sa Accuracy na training a testing sete


VSTUPY
clf - clasifier
parameters - na hladanie v gridsearchu
indf - dataframe s featurmi a targetom spolu
featurenames - list feature nazvov v dataframe, kt. sa maju pouzit
targetname - list target nazvov v dataframe
standardize - ci sa maju normalizovat data
train_size - kolko % ma byt training setu

OUTPUT
clf - najlepsi clasifier fitovany na celom training sete
Xtrain, ytrain, Xtest, ytest - X a y training a testing setu
'''
def do_classify(clf, parameters, indf, featurenames, targetname, standardize=False, train_size=0.7):
    subdf=indf[featurenames]
    if standardize:
        subdfstd=(subdf - subdf.mean())/subdf.std()
    else:
        subdfstd=subdf
    X=subdfstd.values
    y=indf[targetname].values
    Xtrain, Xtest, ytrain, ytest = train_test_split(X, y, train_size=train_size)
    clf = cv_optimize(clf, parameters, Xtrain, ytrain)
    clf=clf.fit(Xtrain, ytrain)
    training_accuracy = clf.score(Xtrain, ytrain)
    test_accuracy = clf.score(Xtest, ytest)
    print ("Accuracy on training data: %0.2f" % (training_accuracy))
    print ("Accuracy on test data:     %0.2f" % (test_accuracy))
    return clf, Xtrain, ytrain, Xtest, ytest


def train_best(clf, parameters, indf, featurenames, targetname, standardize=False):
    subdf=indf[featurenames]
    if standardize:
        subdfstd=(subdf - subdf.mean())/subdf.std()
    else:
        subdfstd=subdf
    X=subdfstd.values
    y=indf[targetname].values
    clf = cv_optimize(clf, parameters, X, y)
    clf=clf.fit(X, y)
    training_accuracy = clf.score(X, y)
##    test_accuracy = clf.score(Xtest, ytest)
    print ("Accuracy on training data: %0.2f" % (training_accuracy))
##    print ("Accuracy on test data:     %0.2f" % (test_accuracy))
    return clf



def modelfit(alg, dtrain, predictors, target, performCV=True, printFeatureImportance=True, cv_folds=5):
    #Fit the algorithm on the data
    alg.fit(dtrain[predictors], dtrain[target])
        
    #Predict training set:
    dtrain_predictions = alg.predict(dtrain[predictors])
    dtrain_predprob = alg.predict_proba(dtrain[predictors])[:,1]
    
    #Perform cross-validation:
    if performCV:
        cv_score = cross_validation.cross_val_score(alg, dtrain[predictors], dtrain[target], cv=cv_folds, scoring='accuracy')
    
    #Print model report:
    print ("\nModel Report")
    print ("Accuracy : %.4g" % metrics.accuracy_score(dtrain[target].values, dtrain_predictions))
    print ("AUC Score (Train): %f" % metrics.roc_auc_score(dtrain[target], dtrain_predprob))
    
    if performCV:
        print ("CV Score : Mean - %.7g | Std - %.7g | Min - %.7g | Max - %.7g" % (np.mean(cv_score),np.std(cv_score),np.min(cv_score),np.max(cv_score)))
        
    #Print Feature Importance:
    if printFeatureImportance:
        feat_imp = pd.Series(alg.feature_importances_, predictors).sort_values(ascending=False)
        feat_imp.plot(kind='bar', title='Feature Importances')
        plt.ylabel('Feature Importance Score')
        plt.show()
        
        
    


train = pd.read_csv("train_u6lujuX_CVtuZ9i.csv")
test = pd.read_csv("test_Y3wMUE5_7gLdaTN.csv")
train['source']='train'
test['source']='test'

# vyhodenie doleziteho infa z training setu mierne pohorsilo/nechalo rovnake
##train = train[ pd.notnull(train['LoanAmount']) ]
##train = train[ pd.notnull(train['Loan_Amount_Term']) ]

df = pd.concat([train, test], ignore_index=True)

print(df.describe())

# frekvency of non-numerical values
df['Property_Area'].value_counts()


#  study distribution of various variables
##df['ApplicantIncome'].hist(bins=50)
##plt.show()
##df.boxplot(column='ApplicantIncome')
##df.boxplot(column='ApplicantIncome', by = 'Education')
##plt.show()

df['Loan_Status'] = df['Loan_Status'].apply(lambda x: 1 if x=='Y' else 0)

# percenta ludi co dostali pozicku ked mali/nemali Credit_History
##print(df.pivot_table(index='Credit_History', values='Loan_Status' ))

# alternativa v jednom kroku (z Y/N na 1/0 + pivottable)
##df.pivot_table(values='Loan_Status',index=['Credit_History'],aggfunc=lambda x: x.map({'Y':1,'N':0}).mean())

#----------------------------Data Munging -------------------------------------------------
#----------fill missing values--------------
# kontrola missing values
missed = df.apply(lambda x: sum(x.isnull()),axis=0)
print(missed)

# nahradenie NaN priemerom
##df['LoanAmount'].fillna(df['LoanAmount'].mean(), inplace=True)

# anmiesto NaN v LoanAmount idem doplnit mediany podla LoanAmount vo Education a Self_Employed, najprv ale doplnim NaN v nich.

# kedze vacsina ludi nieje Self_Employed, tak za Nan doplnim NO
##df['Self_Employed'].value_counts()
df['Self_Employed'].fillna('No',inplace=True)


# median LoanAmountu podla Self_Employed Education
table = df.pivot_table(values='LoanAmount', index='Self_Employed' ,columns='Education', aggfunc=np.median)
# Define function to return value of this pivot_table
def fage(x):
    return table.loc[x['Self_Employed'],x['Education']]

# Replace missing values
##df = df[ pd.notnull(df['LoanAmount']) ]
df['LoanAmount'].fillna(df[df['LoanAmount'].isnull()].apply(fage, axis=1), inplace=True)


# ideme sledovat frekvenciu kategorii
#Filter categorical variables
categorical_columns = [x for x in df.dtypes.index if df.dtypes[x]=='object']
#Exclude ID cols and source:
categorical_columns = [x for x in categorical_columns if x not in ['Loan_ID']]
#Print frequency of categories
for col in categorical_columns:
    print ('\nFrequency of Categories for varible %s'%col)
    print (df[col].value_counts())



# ako baseline vsade vlozime najcastejsiu hodnotu
df['Gender'].fillna('Male',inplace=True)
df['Married'].fillna('Yes',inplace=True)
df['Dependents'].fillna('0',inplace=True)
df['Loan_Amount_Term'].fillna(360,inplace=True)
##df = df[ pd.notnull(df['Loan_Amount_Term']) ]

# volim podla vyslednej pozicky, kedze tam je velka korelacia - toto viedlo k nezmyselnemu overfitovaniu
##df['Credit_History'].fillna(df[df['Credit_History'].isnull()]['Loan_Status'], inplace=True)
df['Credit_History'].fillna(2, inplace=True)

# --------extreme values-----------
# velke pozicky su mozne, tak namiesto vylucenia ako outlier rozdelenie zlogaritmujeme, aby sme znizili ich extremny vplyv.
df['LoanAmount_log'] = np.log(df['LoanAmount'])

# rozdelenie sa teraz podoba viac normalnemu
##df['LoanAmount_log'].hist(bins=20)


# pre income sme spravili sucet ApplicantIncome a CoapplicantIncome a zlogaritmovali
df['TotalIncome'] = df['ApplicantIncome'] + df['CoapplicantIncome']
df['TotalIncome_log'] = np.log(df['TotalIncome'])
##df['LoanAmount_log'].hist(bins=20)
##plt.show()


# --------------------------feature engineering------------
df['LoanTotalIncome_ratio_logs'] = df['LoanAmount_log']/df['TotalIncome_log']
df['LoanTotalIncome_ratio'] = df['LoanAmount']/df['TotalIncome']
df['paidMonthlyTotalIncome_ratio'] = df['LoanAmount']/df['Loan_Amount_Term']*1000/df['TotalIncome']
df['paidMonthlyTotalIncome_ratio_logs'] = df['LoanAmount_log']/df['Loan_Amount_Term']*1000/df['TotalIncome_log']


#----------------------------building model--------------------
# categorical variables into numeric
var_mod = ['Gender','Married','Dependents','Education','Self_Employed','Property_Area','Loan_Status']
##
##for i in df.columns:
##   if not i in var_mod+['Loan_ID', 'source']:
##       df[i] = scale(df[i])
##       


le = LabelEncoder()
for i in var_mod:
    df[i] = le.fit_transform(df[i])

# dodatocny feature engineering
df['paidMonthlyTotalIncome_ratio_timesDeti'] = df['paidMonthlyTotalIncome_ratio']*(df['Dependents']+0)
##df['paidMonthlyTotalIncome_ratio_timesDom'] = df['paidMonthlyTotalIncome_ratio']*(df['Education']+1)*(df['Married']+1)

###One Hot Coding:
df = pd.get_dummies(df, columns=['Credit_History'])




print(df.dtypes)

df_train = df[ df['source']== 'train' ]
df_test = df[ df['source']== 'test' ]



# --------------------LogReg--------------------------------------
# clf = LogisticRegression()
# parameters = {"C": [0.01, 0.1, 1, 10, 100]}
# predictors = [ i for i in df.columns if not i in ['Loan_ID', 'Loan_Status', 'LoanTotalIncome_ratio', 'paidMonthlyTotalIncome_ratio', 'source'] ]
# targetname = 'Loan_Status'
# bestcv, Xtrain, ytrain, Xtest, ytest = do_classify(clf, parameters, df_train, predictors, targetname, standardize=False, train_size=0.7)


# # trening 
# print('trening na celom sete')

# clf_best = train_best(clf, parameters, df_train, predictors, targetname, standardize=False)


# #Predict on testing data:
# df_test['target'] = clf_best.predict(df_test[predictors])
# df_test['target'] = df_test['target'].apply(lambda x: 'Y' if x==1 else 'N')

# submission = pd.DataFrame()
# submission['Loan_ID'] = df_test['Loan_ID']
# submission['Loan_Status'] = df_test['target']
# submission.to_csv('submission_LogReg.csv', index=False)

# --------------------SVM--------------------------------------
# treba znormalizovat, lebo inak trva dlho
# clf = clfsvm = SVC(kernel="linear")
# # parameters = {"C": [ 0.01, 0.1, 1, 10]}
# parameters = {"C":  [1.0]}
# predictors = [ i for i in df.columns if not i in ['Loan_ID', 'Loan_Status', 'LoanTotalIncome_ratio', 'paidMonthlyTotalIncome_ratio', 'source'] ]
# targetname = 'Loan_Status'
# bestcv, Xtrain, ytrain, Xtest, ytest = do_classify(clf, parameters, df_train, predictors, targetname, standardize=False, train_size=0.7)


# # trening 
# print('trening na celom sete')

# clf_best = train_best(clf, parameters, df_train, predictors, targetname, standardize=False)


# #Predict on testing data:
# df_test['target'] = clf_best.predict(df_test[predictors])
# df_test['target'] = df_test['target'].apply(lambda x: 'Y' if x==1 else 'N')

# submission = pd.DataFrame()
# submission['Loan_ID'] = df_test['Loan_ID']
# submission['Loan_Status'] = df_test['target']
# submission.to_csv('submission_SVM.csv', index=False)

# --------------------GBM--------------------------------------
##clf = GradientBoostingClassifier()
##predictors = [ i for i in df.columns if not i in ['Loan_ID', 'Loan_Status', 'LoanTotalIncome_ratio', 'paidMonthlyTotalIncome_ratio', 'source'] ]
predictors = [ i for i in df.columns if not i in ['Loan_ID', 'Loan_Status', 'LoanTotalIncome_ratio', 'paidMonthlyTotalIncome_ratio', 'source'] ]
targetname = 'Loan_Status'
##parameters = {'n_estimators':list(range(5,30,10))}

#clf_best = train_best(clf, parameters, df_train, predictors, targetname, standardize=False)


##modelfit(clf, df_train, predictors, targetname, performCV=True, printFeatureImportance=True, cv_folds=5)

# ideme zistovant number of trees. Ostatne sme zvolili predbezne a intuitivne.
# n_jobs mi na tomto PC funguje len ked je 1

## najlepsi je n_estimators=80 (alternativa 50)
##param_test1 = {'n_estimators':list(range(40,101,10))}
##estimator = GradientBoostingClassifier(learning_rate=0.1, min_samples_split=1,min_samples_leaf=50,max_depth=8,max_features='sqrt',subsample=0.8,random_state=10)
##gsearch1 = GridSearchCV(estimator = estimator, param_grid = param_test1,n_jobs=1,iid=False, cv=5)
##gsearch1.fit(df_train[predictors],df_train[targetname])
##print(gsearch1.grid_scores_, gsearch1.best_params_, gsearch1.best_score_)


## najlepsie je min_samples_split=1 a max_depth=6 (alter 1 a 5)
##param_test2 = {'max_depth':list(range(2,8,1)), 'min_samples_split':list(range(1,5,1))}
##estimator = GradientBoostingClassifier(n_estimators= 130, learning_rate=0.1, min_samples_leaf=50,max_features='sqrt',subsample=0.8,random_state=10)
##gsearch2 = GridSearchCV(estimator = estimator, param_grid = param_test2,n_jobs=1,iid=False, cv=5)
##gsearch2.fit(df_train[predictors],df_train[targetname])
##print(gsearch2.grid_scores_, gsearch2.best_params_, gsearch2.best_score_)

#### najlepsie je min_samples_split=1 a min_samples_leaf=50
##param_test3 = {'min_samples_split':list(range(1,4,1)), 'min_samples_leaf':list(range(30,71,10))}
##estimator = GradientBoostingClassifier(n_estimators= 120, learning_rate=0.1,max_depth=5,max_features='sqrt',subsample=0.8,random_state=10)
##gsearch3 = GridSearchCV(estimator = estimator, param_grid = param_test3,n_jobs=1,iid=False, cv=5)
##gsearch3.fit(df_train[predictors],df_train[targetname])
##print(gsearch3.grid_scores_, gsearch3.best_params_, gsearch3.best_score_)


# max_features=3 (alter. 4)
##param_test4 = {'max_features':list(range(2,8,1))}
##estimator = GradientBoostingClassifier(n_estimators= 50, learning_rate=0.1, min_samples_split=1, max_depth=5,min_samples_leaf=50,subsample=0.8,random_state=10)
##gsearch4 = GridSearchCV(estimator = estimator, param_grid = param_test4,n_jobs=1,iid=False, cv=5)
##gsearch4.fit(df_train[predictors],df_train[targetname])
##print(gsearch4.grid_scores_, gsearch4.best_params_, gsearch4.best_score_)


# subsample = 0.8
##param_test5 = {'subsample':[ 0.8, 0.85, 0.9, 0.95, 0.1]}
##estimator = GradientBoostingClassifier(n_estimators= 50, learning_rate=0.1, min_samples_split=1, max_depth=5,min_samples_leaf=50,random_state=10,max_features=4)
##gsearch5 = GridSearchCV(estimator = estimator, param_grid = param_test5,n_jobs=1,iid=False, cv=5)
##gsearch5.fit(df_train[predictors],df_train[targetname])
##print(gsearch5.grid_scores_, gsearch5.best_params_, gsearch5.best_score_)




# proporcionalne znizim learning rate a zvysim pocet stromov - vyzera ze najlepsie je klasika povodny

##gbm_tuned_0 = GradientBoostingClassifier(learning_rate=0.1, n_estimators=50,max_depth=5, min_samples_split=1,min_samples_leaf=50, subsample=0.8, random_state=10, max_features=4)
##modelfit(gbm_tuned_0, df_train, predictors, targetname, performCV=True, printFeatureImportance=True, cv_folds=5)


##gbm_tuned_1 = GradientBoostingClassifier(learning_rate=0.05, n_estimators=100,max_depth=5, min_samples_split=1,min_samples_leaf=50, subsample=0.8, random_state=10, max_features=4)
##modelfit(gbm_tuned_1, df_train, predictors, targetname, performCV=True, printFeatureImportance=True, cv_folds=5)


##gbm_tuned_2 = GradientBoostingClassifier(learning_rate=0.2, n_estimators=25,max_depth=5, min_samples_split=1,min_samples_leaf=50, subsample=0.8, random_state=10, max_features=4)
##modelfit(gbm_tuned_2, df_train, predictors, targetname, performCV=True, printFeatureImportance=True, cv_folds=5)


##gbm_tuned_3 = GradientBoostingClassifier(learning_rate=0.01, n_estimators=500,max_depth=5, min_samples_split=1,min_samples_leaf=50, subsample=0.8, random_state=10, max_features=4)
##modelfit(gbm_tuned_3, df_train, predictors, targetname, performCV=True, printFeatureImportance=True, cv_folds=5)


# skore 0.79861
estimator = GradientBoostingClassifier(n_estimators= 100, learning_rate=0.1, min_samples_split=1, max_depth=5,min_samples_leaf=50, max_features='sqrt',subsample=0.8, random_state=10)

# to co mi vyslo v tunovani najlepsie
##estimator = GradientBoostingClassifier(n_estimators= 50, learning_rate=0.1, min_samples_split=1, max_depth=5,min_samples_leaf=50, max_features=4,subsample=0.8, random_state=10)

##estimator = GradientBoostingClassifier(n_estimators= 80, learning_rate=0.1, min_samples_split=1, max_depth=6,min_samples_leaf=50, max_features='sqrt',subsample=0.8, random_state=10)
estimator.fit(df_train[predictors], df_train[targetname])
df_test['target'] = estimator.predict(df_test[predictors])
modelfit(estimator, df_train, predictors, targetname, performCV=True, printFeatureImportance=True, cv_folds=5)



#------toto nieje nic--------
##Predict on testing data:
##df_test['target'] = clf_best.predict(df_test[predictors])
#----------------------


df_test['target'] = df_test['target'].apply(lambda x: 'Y' if x==1 else 'N')
submission = pd.DataFrame()
submission['Loan_ID'] = df_test['Loan_ID']
submission['Loan_Status'] = df_test['target']
submission.to_csv('submission_GBM.csv', index=False)
