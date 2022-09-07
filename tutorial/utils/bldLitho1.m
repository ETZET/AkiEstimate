function [vPGrid,vSGrid,rhoGrid,thckGrid,longrid,latgrid] = ...
    bldLitho1(lonvec,latvec)
% 
% Function to construct a velocity model, using LITHO1.0, across a given
% set of longitude and latitude points. 
% 
% INPUTS
% lonvec : Vector of longitude values, in degrees, with one or more points
% latvec : Vector of latitude values, in degrees, with one or more points
% 
% OUTPUTS
% vPGrid : Grid of P-wave velocities, in m/s and in the format: 
%          # layers x # longitude points x # latitude points
% 
% vSGrid : Grid of S-wave velocities, in the same units and format as the 
%          P-wave velocities
% rhoGrid : Grid of densities, in kg/m^3 and in the same format as the 
%           P-wave velocities
% thckGrid : Grid of layer depths, in m and in the same format as the 
%            P-wave velocities
% longrid : 2D grid of longitude values, in degrees
% latgrid : 2D grid of latitude values, in degrees
% 
% Last Modified: June 22, 2021 by Yuri Tamama
% 
% Original author of this code is Tolulolpe Olugboji. This code is 
% modified to accept vectors of latitude and longitude, instead of 
% a range of points. 
% 
% Note: if only one longitude and latitude value are given, then this code
%       will return a velocity model for only one point. 
% 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Check lengths of vectors
if length(lonvec) ~= length(latvec)
  error('Longitude and latitude values must be the same length')
end

% Number of layers and points
totLayers = 9;
numpts=length(lonvec);

% Construct a grid of latitude, longitude if we had more than one point
if numpts > 1
  [latgrid, longrid] = meshgrid(latvec, lonvec);
  % Construct velocity, density, depth grids for each point we want
  vPGrid = zeros([totLayers,size(latgrid)]);
  vSGrid = zeros([totLayers,size(latgrid)]);
  rhoGrid = zeros([totLayers,size(latgrid)]);
  thckGrid = zeros([totLayers,size(latgrid)]);

% Else: construct a vector
else
  latgrid=0;
  longrid=0;
  vPGrid = zeros([totLayers,1]);
  vSGrid = zeros([totLayers,1]);
  rhoGrid = zeros([totLayers,1]);
  thckGrid = zeros([totLayers,1]);
end


% Count variable
iCnt = 1; close all force
maxLyr = 1; minLyr = 8;
maxIntf = ''; minIntf = '';
maxModel = []; minModel = '';


% Iterate through each coordinate and get the velocity model
for ilat = 1: numpts
    for ilon = 1: numpts
        
        % Retrieve the longitude and latitude points
        lon = lonvec(ilon);
        lat = latvec(ilat);
        
        runBin = '/scratch/tolugboj_lab/softwares/litho/1.0/bin/';
        runCmd = [runBin 'access_litho -p ' num2str(lat) '  ' num2str(lon)];
        runCmd2 = [runCmd '| awk ''{print $10}'''];

        %[~, output] = system('access_litho -p 12. 34.');
        % Outputs LITHO1.0 layers
        [~, output] = system(runCmd);
        % Convert output string to another format using sscanf
        [~, count] = sscanf(output, '%f %f %f %f %f %f %f %f %f %*s');
        % Number of rows
        nRows = count/9; % 9 cols
        [modelVals, ~] = sscanf(output, '%f %f %f %f %f %f %f %f %f %*s', [9, nRows]);

        %[~, outputLabel] = system('access_litho -p 12. 34. | awk ''{print $10}''');
        % Just the layer names
        [~, outputLabel] = system(runCmd2);
        [labels, ~] = sscanf(outputLabel, '%s%c');

        interfaceLabel = strsplit(labels);

        %interfaceLabel(1:nRows)
        %num2str(modelVals')

        indBot = 2;
        lyrDep = flipud( modelVals(1,indBot:end)' ); %1 depth in meters
        rho = flipud( modelVals(2,indBot:end)' ); %2 density in kg/m3
        Vp = flipud( modelVals(3,indBot:end)' ); %3 Vp in m/s
        Vs = flipud( modelVals(4,indBot:end)' ); %4 Vs in m/s

        if (length(lyrDep)<1) || (length(rho)<1) 
          iCnt = iCnt + 1;
          continue;
        end
        if (length(Vp)<1) || (length(Vs)<1) 
          iCnt = iCnt + 1;
          continue;
        end

        lyrDep = lyrDep - lyrDep(1);% make top layer zero

        % Thicknesses of Layers
        thickAll = lyrDep(2:end) - lyrDep(1:end-1);
        % Which ones are actual layers and not just boundaries?
        indLyr = thickAll ~= 0;

        % Get thicknesses, density, and velocities for each layer
        thickLyr = thickAll(indLyr);
        rhoLyr = rho(indLyr);
        VpLyr = Vp(indLyr);
        VsLyr = Vs(indLyr);

        % How many layers?
        numLyr = sum(indLyr);
        % load into entire grid, depending on the dimensions
        if numpts > 1
          vPGrid(1:numLyr, ilon, ilat) = VpLyr;
          vSGrid(1:numLyr, ilon, ilat) = VsLyr;
          rhoGrid(1:numLyr, ilon, ilat) = rhoLyr;
          thckGrid(1:numLyr, ilon, ilat) = thickLyr;
        else
          vPGrid(1:numLyr, 1) = VpLyr;
          vSGrid(1:numLyr, 1) = VsLyr;
          rhoGrid(1:numLyr, 1) = rhoLyr;
          thckGrid(1:numLyr, 1) = thickLyr;
        end


        if numLyr > maxLyr
            maxLyr = numLyr;
            maxIntf = interfaceLabel;
            maxModel = [thickLyr, rhoLyr, VpLyr, VsLyr];
        end

        if numLyr < minLyr
            minLyr = numLyr;
            minIntf = interfaceLabel;
            minModel = [thickLyr, rhoLyr, VpLyr, VsLyr];
        end

        %plot(Vp, lyrDep ./ 1e3, Vs, lyrDep ./1e3)
        %hold on

        % Update count
        iCnt = iCnt + 1;
    end
end



