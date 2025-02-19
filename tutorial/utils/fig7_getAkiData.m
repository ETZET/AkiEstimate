%  ------- Plot Figure7: Visualization of Phase Velocity --------  %

%% read in the station list
% stagreater2000km.txt contains all station pairs with dist > 2000km
% staless2000km.txt contains all station pairs with dist <= 2000km

PairList = '/scratch/tolugboj_lab/Prj5_HarnomicRFTraces/2_Data/GE_less2000.csv';
A = readtable(PairList, 'Filetype','text');
sta1 = A{:,'net_sta1'}; 
sta2 = A{:,'net_sta2'};
clear PairList A

%% read in the Aki01 zero-crossing fitted phase velocity
predlove = [];  % store all pred phase vel. by columns
record=[];
for i = 1:length(sta1)
    [i]
    try
    filename = ['/scratch/tolugboj_lab/Prj5_HarnomicRFTraces/AkiEstimate/tutorial/Result/GE/02_Result/Initial_',sta1{i},'_',sta2{i},'/opt.pred-rayleigh'];
    
    if isfile(filename)
        dat = readmatrix(filename, 'Filetype','text');
        freq = dat(:,1);  % third column is the predicted phase velocity
        %pv = dat(:,2);
        
        if length(freq) == 7200
            %predlove = [predlove, pv];
            record = [record, i];
        end
    end
    catch
        %disp([sta1(i), '_', sta2(i), 'Bad Bad.']);
    end
end
predlove = predlove./1000;

%% read in the final uncertanity of Aki phase velocity prediction 
preduncer = [];  % store all uncertanities by columns
record = [];
for i = 1:length(sta1)
    try
        
    filepath = ['/scratch/tolugboj_lab/Prj5_HarnomicRFTraces/AkiEstimate/tutorial/R3_Uncer/R3_Uncer_02/Rayleigh_Uncer/Final_',sta1{i},'_',sta2{i},'.csv'];
    filedir = dir(filepath);
    
    if isempty(filedir)
        continue
    end
    
    dat = readmatrix(filepath, 'Filetype','text');
    upper = dat(:,2);  % the upper bound
    lower = dat(:,3);  % the lower bound
    
    if length(upper) == 2521
        pairuncer = (upper-lower)./4;  % to get the standard deviation
        preduncer = [preduncer, pairuncer];
        record = [record, i];
    end
    
    catch
        disp([sta1(i), '_', sta2(i), 'Bad Bad.']);
    end
end


%% read in the Aki03 predicted phase velocity
predlove = [];  % store all pred phase vel. by columns
record = [];
for i = 1:length(sta1)
    try
    filepath = ['/scratch/tolugboj_lab/Prj5_HarnomicRFTraces/AkiEstimate/tutorial/ResultOf03_Ray/ResultOf03_02/Final_',sta1{i},'_',sta2{i},'/opt.pred-rayleigh'];
    filedir = dir(filepath);
    
    if isempty(filedir)
        continue
    end
    
    dat = readmatrix(filepath, 'Filetype','text');
    pairlove = dat(:,3);  % third column is the predicted phase velocity
    
    if length(pairlove) == 7200
        predlove = [predlove, pairlove];
        record = [record, i];
    end
    
    catch
        disp([sta1(i), '_', sta2(i), 'Bad Bad.']);
    end
end
predlove = predlove./1000;


%% Convert the PV curves into a matrix for heatmap (need Aki03 predicted phase velocity)

% read in the frequency 
filepath = '/scratch/tolugboj_lab/Prj5_HarnomicRFTraces/AkiEstimate/tutorial/ResultOf03/ResultOf03_02/Final_XD-RUNG_XD-MTAN/opt.pred-rayleigh';
dat = readmatrix(filepath, 'Filetype','text');
freq = dat(:,1);  % read in frequence from the first column

% create the matrix: x(freq)* y(phase velocity)
y = linspace(0,7,140);
[~,counts] = size(predlove);
heatpv = zeros(length(y), length(freq));

for i = 1:counts  % iterate through each station pair (column)
    for j = 1: length(freq)   % iterate through each freq (row)
        
        maxpv = max(y(y <= predlove(j,i)));
        maxindex = find(y == maxpv);
        
        heatpv(maxindex,j) = heatpv(maxindex,j) + 1;
    end
end
