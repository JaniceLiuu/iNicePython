//
// Created by jianfei on 20-5-29.
//

#include <stdio.h>

typedef void (*LossFunType)(double *, double *, int);
// void LossFun(double *xInit, double *xOutputSolution, int n)
// void gamma_ll(double *thetaInit, double * thetaSolution, int n)  c-end callback python-end, where
//theta is double [n],

void nlmSimple(LossFunType f, double* xInit, double* xOutput, int n) {

    //print input initial data
    int i=0;
    for(; i<n; ++i) {
        printf("%f, ", xInit[i]);
    }

    //test if we can call into the python-end with toy data
    i=0;
    for(; i<n; ++i) {
        xOutput[i] = i;           //toy solution
    }

    (*f)(xInit, xOutput, n);
}