import ctypes
from numpy.ctypeslib import ndpointer
import numpy as np
import math

class nlmMinimizer:

    def __init__(self, xInit, lossMemberFun, c_print_level=0):
        self.lossMemberFun = lossMemberFun
        self.xInit = xInit
        self.xOuput = np.ones(self.xInit.size, dtype=np.float64)
        self.code = ctypes.c_int(0)
        self.iterCount = ctypes.c_int(0)
        self.retValue = 0

        # typedef double (*LossFunType)(const double *x, unsigned long n);
        #
        # double nlm_simple(LossFunType f, double* xInit,
        #         unsigned long n, double* xOutput, int* resultCode, int* iterCount,
        #         double *c_typsize, double c_fscale, int c_print_level,
        #         int c_ndigit, double c_gradtol,
        #         int c_stepmax, double c_steptol,
        #         int c_iterlim, bool c_check_analyticals);

        self.c_typsize = np.ones(self.xInit.size, dtype=np.float64)
        self.c_fscale = 1.0
        self.c_print_level = c_print_level  # must be in {0,1,2}
        self.c_ndigit = 12
        self.c_gradtol = 1e-06
        self.c_steptol = 1e-06
        self.c_iterlim = 100
        self.c_check_analyticals = True
        # c_stepmax = max(1000 * sqrt( sum((xInit/typsize)^2) ), 1000),
        xs = self.xInit / self.c_typsize
        s = sum( xs ** 2)
        self.c_stepmax = max(int(1000.0 * math.sqrt(s)), 1000)

        # print('DEB: ..start.lib.CDLL')
        lib = ctypes.CDLL("./libnlm_simple.so")
        # print('DEB: ...lib.CDLL')

        self.fun = lib.nlm_simple
        self.fun.restype = ctypes.c_double
        self.callBackType = ctypes.CFUNCTYPE(ctypes.c_double,
                                   ctypes.POINTER(ctypes.c_double),
                                   ctypes.c_ulong)
        self.fun.argtypes = [self.callBackType,
                        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
                        ctypes.c_ulong,
                        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
                        ctypes.POINTER(ctypes.c_int),
                        ctypes.POINTER(ctypes.c_int),
                        ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"), # c_typsize
                        ctypes.c_double, # double c_fscale
                        ctypes.c_int, # int c_print_level
                        ctypes.c_int, # int c_ndigit
                        ctypes.c_double, # double c_gradtol
                        ctypes.c_int, # int c_stepmax
                        ctypes.c_double, # double c_steptol
                        ctypes.c_int, # int c_iterlim
                        ctypes.c_bool # bool c_check_analyticals
                        ]

        # void optcode(int code)
        self.optcode = lib.optcode
        self.optcode.argtypes = [ctypes.c_int]

    # typedef double (*LossFunType)(const double *xOutput, unsigned long n);
    def __call__(self):
        # double nlm_simple(LossFunType f, double* xInit,
        #         unsigned long n, double* xOutput, int* resultCode, int* iterCount,
        #         double *c_typsize, double c_fscale, int c_print_level,
        #         int c_ndigit, double c_gradtol,
        #         int c_stepmax, double c_steptol,
        #         int c_iterlim, bool c_check_analyticals);
        cb = self.callBackType (lambda x, n: self.lossMemberFun(
                                            np.array([x[i] for i in range(n)])
                                            )
                                )
        self.retValue = None
        # print('DEB: starting call self.fun....')
        try:
            self.retValue = self.fun(cb,
                                     self.xInit,
                                     self.xInit.size,
                                     self.xOuput,
                                     ctypes.byref(self.code),
                                     ctypes.byref(self.iterCount),
                                     self.c_typsize,
                                     self.c_fscale,
                                     self.c_print_level,
                                     self.c_ndigit,
                                     self.c_gradtol,
                                     self.c_stepmax,
                                     self.c_steptol,
                                     self.c_iterlim,
                                     self.c_check_analyticals)

            # print('DEG: end of calling self.fun...retVal=',self.retValue)
            return True, self.retValue
        except Exception as e:
            print('nlm_simple throw an exception: ', e)
            return False, self.retValue

    def showResult(self):
        print('xInit =', self.xInit)
        print('xOuput = ', self.xOuput)
        print('code =', self.code.value)
        self.optcode(self.code)

        print('iterCount =', self.iterCount.value)
        print('retValue = ', self.retValue)

    def getXSolution(self):
        return self.xOuput

    def getRetValue(self):
        return self.retValue

    def getIterCount(self):
        return self.iterCount.value