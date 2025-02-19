function makemdlfiles_litho(connection_file,output)


% add paths
%addpath '/scratch/tolugboj_lab/Prj6_AfrTomography/X_Bin_copy/parseCrustModels/Src'
filedir=output;

%%

% Read in information
statbl=readtable(connection_file);
startnet=statbl.net1;
startsta=statbl.sta1;
startlats=statbl.lat1;
startlons=statbl.lon1;
% 
stopnet=statbl.net2;
stopsta=statbl.sta2;
stoplats=statbl.lat2;
stoplons=statbl.lon2;
%
[numpairs,~]=size(statbl);  

%%
% FIX THOSE FILES
for p=1:numpairs %numpairs
    
  if mod(p,10) == 0
    fprintf("Progress: %d/%d\n",p,numpairs)
  end
    
  % Get start and end coordinates
  net1=startnet{p};                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
  sta1=startsta{p};
  net2=stopnet{p};
  sta2=stopsta{p};
  
  % Initialize file name
  filename=sprintf('%s-%s_%s-%s.txt',net1,sta1,net2,sta2);
  filename=fullfile(filedir,filename);
  
  % Get average longitude and latitude
  lat1=startlats(p);
  lon1=startlons(p);
  lat2=stoplats(p);
  lon2=stoplons(p);
  avglat=mean([lat1 lat2]);
  avglon=mean([lon1 lon2]);
  
  % Get shear velocity profile and thicknesses
  [~,vsvals,~,thckvals,~,~] = bldLitho1_Tamama(avglon,avglat);
  numlyr=length(vsvals);
  % Convert to km and km/s
  vsvals=vsvals/1000;
  thckvals=thckvals/1000;
  
  % Check for zeroes in velocity model or thicknesses
  numlyrlist=numlyr;
  for i=1:numlyr
    if vsvals(i)==0 || thckvals(i)==0
      numlyrlist=numlyrlist-1;
      if vsvals(i)~= 0 && thckvals(i)==0
        keyboard
      end
    end
  end
  
  % Populate file
  fid=fopen(filename,'w');
  % Number of layers
  fprintf(fid,'%d \n',numlyrlist);
  % Thickness, velocity, and velocity uncertainty at each layer
  lyrcount=0;
  for i=1:numlyr
    % Check for zeroes
    if vsvals(i)==0 || thckvals(i)==0
      % Skip
      continue;
    end
    
    lyrcount=lyrcount+1;
    
    if lyrcount<numlyrlist
      if thckvals(i)<10
        fprintf(fid,'  %.6f 0   %.6f   %.6f\n',thckvals(i),vsvals(i),...
          0.01*vsvals(i));
      elseif thckvals(i)<100
        fprintf(fid,' %.6f 0   %.6f   %.6f\n',thckvals(i),vsvals(i),...
          0.01*vsvals(i));
      else
        fprintf(fid,'%.6f 0   %.6f   %.6f\n',thckvals(i),vsvals(i),...
          0.01*vsvals(i));
      end
    else
      fprintf(fid,'  %.6f 0   %.6f   %.6f\n',0,vsvals(i),...
        0.01*vsvals(i));
    end
    
  end
  
  % Close file
  fclose(fid);

end

end

% Final file format, for each station pair
% 8
%  10.000000 5   2.677364   2.696691   3.011173   3.452268   3.548123   3.560000   0.198500
%  20.000000 0   3.560000   0.062500
%  20.000000 0   4.220000   0.075000
%  25.000000 0   3.960000   0.075000
%  25.000000 0   3.890000   0.112500
% 110.000000 5   3.995920   4.022732   4.199614   4.308612   4.367944   4.378156   0.150000
% 140.000000 5   4.378156   4.395170   4.465858   4.572088   4.710317   4.800000   0.150000
%   0.000000 0   4.800000   0.150000 


