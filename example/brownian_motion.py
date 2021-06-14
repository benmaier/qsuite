import numpy as np

class BrownianMotion:
    def __init__(self,N, L, T, V, r, tmax, dt, x0 = 0, seed=-1):
        self.N = N
        self.L = L
        self.T = T
        self.dt = dt
        self.factor_B = np.sqrt(2*T*self.dt)
        self.tmax = tmax
        self.x0 = x0

        if seed != -1:
            np.random.seed(seed)

        self.t = np.linspace(0,self.tmax,int(self.tmax/self.dt)+1)
        self.X = np.zeros((len(self.t),self.N))
        self.X[0,:] = x0*np.ones((self.N,))

        self.V = V
        self.r = r

    def simulate(self):
        for t in range(1,len(self.t)):
            self.X[t,:] = self.X[t-1,:] + \
                          self.V*(self.r-self.X[t-1,:]) * self.dt + \
                          self.factor_B * np.random.randn(self.N)
            ndcs_left  = np.nonzero(self.X[t,:] < -self.L/2)[0]
            ndcs_right = np.nonzero(self.X[t,:] > +self.L/2)[0]
            self.X[t,ndcs_left] += self.L
            self.X[t,ndcs_right] -= self.L


    def get_trajectories(self):
        return self.t,self.X


if __name__=="__main__":

    N = 100
    tmax = 10
    dt = 0.01
    T = 1
    V = 1
    r = 0
    L = 1

    sim = BrownianMotion(N=N,L=L,T=T,V=V,r=r,tmax=tmax,dt=dt)
    sim.simulate()

    t,X = sim.get_trajectories()

    import matplotlib.pyplot as pl

    bins = np.linspace(-L/2.,L/2.,11)
    bins_mean = 0.5*(bins[1:]+bins[:-1])

    for t_ in range(len(t)):
        vals,bins = np.histogram(X[t_,:],bins=bins,density=True)
        pl.plot(0.5*(bins[:-1]+bins[1:]),vals)

    pl.show()
