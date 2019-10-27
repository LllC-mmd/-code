import numpy as np
import pandas as pd


class XinAnJiang(object):

    def __init__(self, wu_i, wl_i, wd_i, s_i, qrss_i, qrg_i,
                 wum, wlm, wdm, K, C, B, imp, sm, ex, kg, kss, kkg, kkss,
                 dt, F, n, iuh_value):
        # initial condition
        self.wu = wu_i
        self.wl = wl_i
        self.wd = wd_i
        self.s = s_i
        self.qrss = qrss_i
        self.qrg = qrg_i
        # parameter
        self.wum = wum
        self.wlm = wlm
        self.wdm = wdm
        self.wm = self.wum+self.wlm+self.wdm
        self.K = K
        self.C = C
        self.B = B
        self.imp = imp
        self.wwmm = (1+self.B)*self.wm/(1-self.imp)
        self.sm = sm
        self.ex = ex
        self.ssm = self.sm*(1+self.ex)
        self.kg = kg
        self.kss = kss
        self.kkg = kkg
        self.kkss = kkss
        # simulation settings
        self.dt = dt
        self.n = n
        self.F = F
        self.iuh = iuh_value
        self.lh = len(iuh_value)
        self.ic = 0
        self.rsBlock = np.zeros(self.lh, dtype=np.float)
        self.rssBlock = np.array([self.qrss, 0], dtype=np.float)
        self.rgBlock = np.array([self.qrg, 0], dtype=np.float)
        self.u = 10 * self.F / (3.6 * self.dt)  # convert depth to flow
        # outflow result
        self.Qs = np.zeros(n)
        self.Qss = np.zeros(n)
        self.Qg = np.zeros(n)

    def step(self, p, ep):
        # effective precipitation
        em = self.K*ep
        pe = p - em
        # flood ratio
        self.wu = min(self.wu, self.wum)
        self.wl = min(self.wl, self.wlm)
        self.wd = min(self.wd, self.wdm)
        w = self.wu+self.wl+self.wd
        fr = 1 - np.power(1 - w/self.wm, self.B/(1+self.B))
        # runoff summation
        wwm = self.wwmm*(1 - np.power(1-w/self.wm, 1/(1+self.B)))
        if pe + wwm >= self.wwmm:
            r = pe - (self.wm - w)
        elif pe >= 0:
            r = pe - (self.wm - w - self.wm*np.power(1-(pe+wwm)/self.wwmm, 1+self.B))
        else:
            r = 0
        # runoff division
        if pe <= 0:
            rs = 0
            rss = self.kss * self.s * fr
            rg = self.kg * self.s * fr
        else:
            if pe + self.s <= self.ssm:
                ds = self.sm - self.s - self.sm*np.power(1-(pe+self.s)/self.ssm, 1+self.ex)
            else:
                ds = self.sm - self.s
            s_next = self.s + ds
            rs = (pe-ds)*fr
            rss = self.kss * s_next * fr
            rg = self.kg * s_next * fr
            # update free surface water
            self.s = (1-self.kss-self.kg)*s_next
        rs = rs*(1-self.imp)
        rss = rss*(1-self.imp)
        rg = rg*(1-self.imp)
        # update surface runoff block
        self.rsBlock[1:self.lh] = self.rsBlock[0:self.lh-1]
        self.rsBlock[0] = rs
        # update subsurface runoff block
        self.rssBlock[1] = self.rssBlock[0]
        self.rssBlock[0] = rss
        # update groundwater runoff block
        self.rgBlock[1] = self.rgBlock[0]
        self.rgBlock[0] = rg
        # Update the storage of all layers considering evaporation
        self.w_update(p, em, r)
        # flow
        self.iuh_route()
        # End
        self.ic += 1

    def w_update(self, p, em, r):
        # When pe > 0, we should increase w from up to down
        # The maximum storage of all layers should be considered
        pe = p - em
        if pe > 0:
            dw = pe - r
            if self.wu + dw <= self.wum:
                self.wu += pe - r
            elif self.wl + dw - (self.wum-self.wu) <= self.wlm:
                self.wu = self.wum
                self.wl += dw - (self.wum-self.wu)
            else:
                self.wu = self.wum
                self.wl = self.wlm
                self.wd = min(self.wdm, self.wd+dw-(self.wum-self.wu)-(self.wlm-self.wl))
        # When pe < 0, we should decrease w from top to down
        # The storage of all layers should be kept non-negative
        # Note r = 0
        else:
            # Upper evaporation is control by the capability of evaporation, i.e., em
            if self.wu + pe >= 0:
                self.wu += pe
            # Upper evaporation is control by the storage of water
            # Assume: e/em = w/wm, where em = "remaining capability of evaporation"
            else:
                eu = self.wu + p
                em_r = em - eu
                self.wu = 0
                # No evaporation for the deep layer
                if self.wl >= self.C*self.wlm:
                    el = em_r*self.wl/self.wlm
                    self.wl = max(0, self.wl - el)
                else:
                    self.wl = 0
                    ed = self.C*em_r - self.wl
                    self.wd = max(0, self.wd - ed)

    def iuh_route(self):
        # surface flow
        for jj in range(0, self.lh):
            self.Qs[self.ic] += self.rsBlock[jj] * self.iuh[jj] * self.u
        # subsurface flow
        self.Qss[self.ic] = self.rssBlock[1]*self.kkss + self.rssBlock[0]*(1-self.kkss)*self.u
        # groundwater flow
        self.Qg[self.ic] = self.rgBlock[1]*self.kkg + self.rgBlock[0]*(1-self.kkg)*self.u

    def save_result(self):
        np.savetxt("Qs.txt", self.Qs, delimiter="\n", fmt='%.3f')
        np.savetxt("Qss.txt", self.Qss, delimiter="\n", fmt='%.3f')
        np.savetxt("Qg.txt", self.Qg, delimiter="\n", fmt='%.3f')
        np.savetxt("Q.txt", self.Qs+self.Qss+self.Qg, delimiter="\n", fmt='%.3f')


if __name__ == '__main__':
    df = pd.read_excel("XinanJiang_test.xlsx")
    p = np.array(df["P"])
    e = np.array(df["Ep"])
    xajModel = XinAnJiang(wu_i=0, wl_i=70, wd_i=80, s_i=20, qrss_i=40, qrg_i=20,
                 wum=20, wlm=75, wdm=80, K=0.65, C=0.11, B=0.3, imp=0, sm=20, ex=1, kg=0.3, kss=0.41, kkg=0.99, kkss=0.6,
                 dt=2, F=537, n=24, iuh_value=[0.3, 0.6, 0.1])
    for i in range(0, 24):
        xajModel.step(p=p[i], ep=e[i])
    xajModel.save_result()
