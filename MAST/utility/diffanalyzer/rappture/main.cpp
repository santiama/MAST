/*
 * ----------------------------------------------------------------------
 *  MAIN PROGRAM - generated by the Rappture Builder
 * ----------------------------------------------------------------------
 */
#include "rappture.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <fstream>
#include <streambuf>
#include <iostream>
#include <time.h>
#include <vector>
#include <gsl/gsl_fit.h>
#include <gsl/gsl_statistics_double.h>

#include <unistd.h>

using namespace std;

static void getInput(string* , int&, int&, vector<int>&, vector<string>&);
static void getPos(string*, int, double, int, int, double[][3]);
static void fixPBC(int, double, int, double[][3]);
static void getR2(int,int,int,int,double[][3],double[][3],double[]);
static void gettimes(int,double,double[]);

char XDATCAR_Path[50] = "/apps/diffanalyzer/current/data/XDATCAR";

int main(int argc, char * argv[])
{
	/* stuff needed for Rappture library */
	RpLibrary* io;
	const char* data; char line[255];
	char line1[255]; char line2[255];
	const char* ptrXDATCAR;
	//int err;

	string* datFile;
	int numAtom;  /* for input.integer(numAtom) */
	double len;  /* for input.number(len) */
	int numStep;  /* for input.integer(numStep) */
	int buffLine;  /* for input.integer(buffLine) */
	double delt;  /* for input.number(delt) */
	int nCut;  /* for input.integer(nCut) */
	int numComp;  /* for input.integer(numComp) */
	char outTable[1024];  /* for output.string(outTable) */
	vector<int> nType;
	vector<string> elemIds;

	/* open the XML file containing the run parameters */
	io = rpLibrary(argv[1]);

	if (io == NULL)
	{
		/* cannot open file or out of memory */
		printf("FAILED loading Rappture data\n");
		exit(1);
	}

	/*
	*********************************************************
	* Get input values from Rappture
	*********************************************************
	*/
	    
	/* get input value for input.number(len) */
	rpGetString(io,"input.number(len).current", &data);
	len = atof(data);
	    
	/* get input value for input.integer(numStep) */
	rpGetString(io,"input.integer(numStep).current", &data);
	numStep = atoi(data);
	    
	/* get input value for input.integer(buffLine) */
	rpGetString(io,"input.integer(buffLine).current", &data);
	buffLine = atoi(data);
	    
	/* get input value for input.number(delt) */
	rpGetString(io,"input.number(delt).current", &data);
	delt = atof(data);
	    
	/* get input value for input.integer(nCut) */
	rpGetString(io,"input.integer(nCut).current", &data);
	nCut = atoi(data);

	// Check if the user uploaded the XDATCAR file.
	rpGetString(io,"input.loader.current", &data);

	if(strcmp(data, "Uploaded data") == 0)
	{
		// Read the XDATCAR file uploaded by the user.
		rpGetString(io,"input.loader.upload.to", &data);
		memset(line, 0, sizeof(line));
		strcat(line, data);
		strcat(line, ".current");
		rpGetString(io,line, &ptrXDATCAR);
		datFile = new string(ptrXDATCAR);
	}
	else
	{
		// User did not upload any XDATCAR file.
		// Load the default XDATCAR file.
		ifstream XDAT(XDATCAR_Path);
		datFile = new string(istreambuf_iterator<char>(XDAT), istreambuf_iterator<char>());
	}

	rpUtilsProgress(0, "Starting...");

	// Read some of the input parameters from the XDATCAR file.
	getInput(datFile, numAtom, numComp, nType, elemIds);

	// Code for dynamically adding the output curves based
	// on the number of elements in the XDATCAR file.

	char xmlPath[300], intBuff[10], label[50], style[50];

	for(int i = 1; i <= numComp; i++)
	{
		for(int j = 0; j < 3; j++)
		{
			if(j == 0)
			{
				sprintf(intBuff, "%d", i);
				sprintf(label, "%s Mean Square Displacement", elemIds.at(i-1).c_str());
				sprintf(style, "-color black -width 2");
			}
			else if(j == 1)
			{
				sprintf(intBuff, "%d%d", i, 1);
				sprintf(label, "MSD - 1 sigma");
				sprintf(style, "-color blue -linestyle dashed");
			}
			else
			{
				sprintf(intBuff, "%d%d", i, 2);
				sprintf(label, "MSD + 1 sigma");
				sprintf(style, "-color blue -linestyle dashed");
			}

			sprintf(xmlPath, "output.curve(curve%s).about.label", intBuff);
			rpPutString(io, xmlPath, label, RPLIB_OVERWRITE);

			sprintf(xmlPath, "output.curve(curve%s).about.description", intBuff);
			rpPutString(io, xmlPath, "Time-Total MSD graph", RPLIB_OVERWRITE);

			sprintf(xmlPath, "output.curve(curve%s).about.style", intBuff);
			rpPutString(io, xmlPath, style, RPLIB_OVERWRITE);

			sprintf(xmlPath, "output.curve(curve%s).xaxis.label", intBuff);
			rpPutString(io, xmlPath, "Time (in seconds)", RPLIB_OVERWRITE);

			sprintf(xmlPath, "output.curve(curve%s).xaxis.description", intBuff);
			rpPutString(io, xmlPath, "Time (in seconds)", RPLIB_OVERWRITE);

			sprintf(xmlPath, "output.curve(curve%s).yaxis.label", intBuff);
			rpPutString(io, xmlPath, "Total MSD (in Angstrom^2)", RPLIB_OVERWRITE);

			sprintf(xmlPath, "output.curve(curve%s).yaxis.description", intBuff);
			rpPutString(io, xmlPath, "Total mean square displacement (in Angstrom^2)", RPLIB_OVERWRITE);

			sprintf(xmlPath, "output.curve(curve%s).about.group", intBuff);
			rpPutString(io, xmlPath, elemIds.at(i-1).c_str(), RPLIB_OVERWRITE);
		}
	}

	delt = delt*1E-15;
	int nTot = numStep/2;
	int nFit = nTot-nCut;	
	int aLow[numComp],aHigh[numComp];
	
	aLow[0] = 0;
	aHigh[0] = nType[0]-1;

	for(int i=1; i<numComp; i++)
	{
		aLow[i] = aHigh[i-1]+1;
		aHigh[i] = aHigh[i-1]+nType[i];
	}

    
	double posData[numAtom*numStep][3],R2[nTot][3],timeVec[nTot],stdev[nTot];
	double R2X[nFit],R2Y[nFit],R2Z[nFit],tFit[nFit],R2p[nFit],R2m[nFit],R2tot[nFit],ewt[nFit];

	getPos(datFile,numAtom,len,numStep,buffLine,posData);

	fixPBC(numAtom,len,numStep,posData);

	gettimes(numStep,delt,timeVec);

	rpUtilsProgress(30, "Processing...");
	
	for(int c=0; c<numComp; c++)
	{
		getR2(aLow[c],aHigh[c],numAtom,numStep,posData,R2,stdev);

		for(int i=0; i<nFit; i++)
		{
			int j = i+nCut;
			R2X[i] = R2[j][0];
			R2Y[i] = R2[j][1];
			R2Z[i] = R2[j][2];
			R2tot[i] = R2[j][0] + R2[j][1] + R2[j][2];
			R2p[i] = R2[j][0] + R2[j][1] + R2[j][2] + stdev[j];
			R2m[i] = R2[j][0] + R2[j][1] + R2[j][2] - stdev[j];
			tFit[i] = timeVec[j]-timeVec[nCut];
			ewt[i] = 1./pow(stdev[j],2);
		}

		ewt[0] = 0;	

		double A2m = 1E-20;
		double slope,intcpt,cv00,cv01,cv11,resNorm;
		gsl_fit_linear(tFit,1,R2X,1,nFit,&intcpt,&slope,&cv00,&cv01,&cv11,&resNorm);
		double DsX = 0.5*slope*A2m;
		gsl_fit_linear(tFit,1,R2Y,1,nFit,&intcpt,&slope,&cv00,&cv01,&cv11,&resNorm);
        	double DsY = 0.5*slope*A2m;
		gsl_fit_linear(tFit,1,R2Z,1,nFit,&intcpt,&slope,&cv00,&cv01,&cv11,&resNorm);
        	double DsZ = 0.5*slope*A2m;

		gsl_fit_wlinear(tFit,1,ewt,1,R2tot,1,nFit,&intcpt,&slope,&cv00,&cv01,&cv11,&resNorm);
		double Derr = 0.5*sqrt(cv11)*A2m/3;

		double DsAv = (DsX+DsY+DsZ)/3;

		sprintf(line, "Element Id: %s\n\nTime\t  x-MSD\t\ty-MSD\t\tz-MSD\t\tTotal MSD\t+/- MSD Error\nseconds\t  Angstrom^2\tAngstrom^2\tAngstrom^2\tAngstrom^2\tAngstrom^2\n", elemIds.at(c).c_str());
		rpPutString(io, "output.string(outTable).current", line, RPLIB_APPEND);		

		for(int i=0; i<nFit; i=i+100)
		{
			double time = tFit[i];
			double totalMSD = R2X[i]+R2Y[i]+R2Z[i];

			// Populate the output curves and table.
			sprintf(intBuff, "%d", c+1);
			sprintf(xmlPath, "output.curve(curve%s).component.xy", intBuff);
			sprintf(line, "%g %g\n", time, totalMSD);
			rpPutString(io, xmlPath, line, RPLIB_APPEND);

			sprintf(intBuff, "%d%d", c+1, 1);		
			sprintf(xmlPath, "output.curve(curve%s).component.xy", intBuff);
			sprintf(line1, "%g %g\n", time, R2m[i]);
			rpPutString(io, xmlPath, line1, RPLIB_APPEND);

			sprintf(intBuff, "%d%d", c+1, 2);		
			sprintf(xmlPath, "output.curve(curve%s).component.xy", intBuff);
			sprintf(line2, "%g %g\n", time, R2p[i]);
			rpPutString(io, xmlPath, line2, RPLIB_APPEND);

			sprintf(line, "%#.02g\t  %#.04f\t%#.04f\t\t%#.04f\t\t%#.04f\t\t%#.04f\n", time, R2X[i], R2Y[i], R2Z[i],totalMSD, R2p[i] - totalMSD);
			rpPutString(io, "output.string(outTable).current", line, RPLIB_APPEND);
		}

		sprintf(outTable, "\nDiffusion coefficients (m^2/sec):\nx-direction\ty-direction\tz-direction\tTotal\t\t+/- MSD Error\n%#.05g\t%#.05g\t%#.05g\t%#.05g\t%#.05g\n\n\n", DsX, DsY, DsZ, DsAv, Derr);
		rpPutString(io, "output.string(outTable).current", outTable, RPLIB_APPEND);
		
		for(int i=0; i<nTot; i++)
		{
			for(int d=0; d<3; d++)
			{
				R2[i][d] = 0;
			}
		}

		rpUtilsProgress((30 + ((c + 1) * 20)), "Processing...");
	}

    rpUtilsProgress(100, "Done");

    delete datFile;
    rpResult(io);
    exit(0);
}

void getInput(string* datFile, int& numAtom, int& numComp, vector<int>& nType, vector<string>& elemIds)
{
	numAtom = 0;
	numComp = 0;

	istringstream XDAT(*datFile);
	string buff;

	for(int i=0; i < 3; i++)
	{
		getline(XDAT,buff);

		if(i == 1 || i == 2)
		{
			char strBuff[200];
			
			strcpy(strBuff, buff.c_str());

			char* substr = strtok(strBuff, " ");

			while(substr != NULL)
			{
				if(i == 1)
				{
					elemIds.push_back(substr);
				}

				if(i == 2)
				{
					nType.push_back(atoi(substr));
					numAtom += nType.back();
					numComp++;
				}

				substr = strtok(NULL, " ");
			}
		}
	}
}

void getPos(string* datFile, int numAtom, double len, int numStep, int buffLine, double posData[][3])
{	
	istringstream XDAT(*datFile);
	string buff;
	int aInd;

	for(int i=0; i<buffLine; i++)
	{
		getline(XDAT,buff);
	}
	
	for(int i=0; i<numStep; i++)
	{
		for(int j=0; j<numAtom; j++)
		{
			aInd = i*numAtom+j;
			for(int d=0; d<3; d++)
			{
				XDAT >> posData[aInd][d];
				posData[aInd][d] = posData[aInd][d]*len;
			}
			getline(XDAT,buff);
		}
		getline(XDAT,buff);
	}
}
		
void fixPBC(int numAtom, double len, int numStep, double posData[][3])
{
	double delta,posOld,delOld;
	int aInd;

	for(int i=1; i<numStep; i++)
	{
		for(int j=0; j<numAtom; j++)
		{
			aInd = i*numAtom+j;	
			for(int d=0; d<3; d++)
			{
				delta = posData[aInd][d]-posData[aInd-numAtom][d];
				if(delta > 0.6*len)
				{
					posOld = posData[aInd][d];
					delOld = delta;
					posData[aInd][d] = posData[aInd][d] - len*round(fabs(delta/len));
				}
				if(delta < -0.6*len)
				{
					posOld = posData[aInd][d];
					delOld = delta;
					posData[aInd][d] = posData[aInd][d] + len*round(fabs(delta/len));
				}
			}
		}
	}
}

void getR2(int aLow, int aHigh, int numAtom, int numStep, double posData[][3], double R2[][3], double stdev[])
{
	int numOrg = int(numStep/2);
	int iInd,fInd;
	int iMin = 1;
	int iMax = int(numStep/2);
	//int aInd;
	double R2tot;

	double* R2stats = new double[iMax * numOrg];
	double R2eacht[numOrg];

	for(int i=aLow; i<aHigh+1; i++)
	{
		for(int j=0; j<numOrg; j++)
		{
			iInd = j*numAtom+i;
			for(int k=iMin; k<iMax; k++)
			{
				fInd = iInd+k*numAtom;
				R2tot = 0;
				for(int d=0; d<3; d++)
				{
					R2[k][d] = R2[k][d] +
					pow((posData[fInd][d]-posData[iInd][d]),2);
					R2tot = R2tot + pow((posData[fInd][d]-posData[iInd][d]),2);
				}
				R2stats[k * iMax + j] = R2stats[k * iMax + j] + R2tot; //add up SD from each atom for timestep k for each origin j
			}
		}
	}

	int nType = (aHigh+1)-aLow;
	for(int k=iMin; k<iMax; k++)
	{
		for(int d=0; d<3; d++)
		{
			R2[k][d] = R2[k][d]/double(nType*numOrg);
		}
	}

	for(int k=iMin; k<iMax; k++)
	{
		for(int j=0; j<numOrg; j++)
		{
			R2eacht[j] = R2stats[k * iMax + j]/double(nType);
			R2stats[k * iMax + j] = 0;
		}
		stdev[k] = gsl_stats_sd(R2eacht,1,iMax);
	}

	delete[] R2stats;
}

void gettimes(int numStep, double delt, double timeVec[]){
	//ifstream timeFile;
	//timeFile.open("timeFile");	// not used
	timeVec[0] = 0.0;
	for(int i=1; i<numStep/2; i++){
		//timeFile >> timeVec[i];
		timeVec[i] = timeVec[i-1]+delt;
	}
	//timeFile.close();

return;
}
