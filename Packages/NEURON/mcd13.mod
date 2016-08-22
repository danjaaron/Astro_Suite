NEURON {

	SUFFIX mcd
	USEION ca READ ica WRITE cai VALENCE 2
	USEION IP3 READ iIP3 WRITE IP3i VALENCE 2
	RANGE rand, eATP, cinit, ipinit, ca_ERinit, hinit, gluinit, eATPinit, ip30, krel, cmin, jatpmax, sdev, kler, klext, gap_cai, gap_IP3i

}

UNITS {

    (mM) = (milli/liter)
    (um) = (micron)
    FARADAY = (faraday) (coulomb)
    PI = (pi) (1)

}

ASSIGNED {

	:: IONS ::
	ica (uM)
	iIP3 (uM)
	
	:: CAI STATE RATES ::
	j_IP3R
	j_SERCA
	j_lER
	j_PCA
	j_lext

	:: IP3i STATE RATES ::
	G_ATP
	G_glu
	pATP
	delta
	pglu
	rand : noise factor from normal dist

	:: STEPS ::
	eATP : extracellular eATP

	:: GAPS ::
	gap_cai
	gap_IP3i

	::: INITIAL VALUES :::

	: states
	cinit
	ipinit
	ca_ERinit
	hinit
	gluinit
	eATPinit

	: parameters
	ip30
	krel 
	cmin 
	jatpmax
	sdev
	kler
	klext

}

PARAMETER {

	::: CA SUBSYSTEM :::
	beta = 0.0244
	cext = 2000 (uM) : may need to access/alter from STEPS
	jip3rmax = 100 (uM/s)
	kc = 0.06 (uM)
	ki = 0.02 (uM)
	koff = 0.75 (uM/s)
	kon = 0.1 (uM)
	jsercamax = 5.8 (uM/s)
	kserca = 0.25 (uM)
	rvol = 5.4
	k1 = 0.08 (uM)
	k2 = 0.38 (uM)
	v1 = 1.63 (uM/s)
	v2 = 31.67 (uM/s)

	::: IP3 SUBSYSTEM :::
	kdeg = 0.8 (1/s)
	rh = 0.02 (uM/um2s)
	katp = 15 (uM)
	kglu = 5 (uM)
	kd = 0.15 (1/s)
	ka = 0.017 (1/s)

	:: GAPS ::
	Pip3 = 3.00 (um/s2)
	Pca = 0.03 (um/s2)
	Dip3 = 280 (um/s2)
	Dca = 20 (um/s2)
}

COMMENT
Gap junction values must already be a flux relative to 
the calculating section, due to some sections being 
connected to many others via gap junctions.
ENDCOMMENT

STATE {

	::: Ion state variables :::

	: Intracellular Calcium (cyto)
	cai 
	: Intracellular IP3
	IP3i
	: Intracellular Calcium (ER)
	ca_ER
	: IP3R gating state variable
	h

	::: Stimulation state variables :::
	
	: Glutamate
	glu
	: Section-produced ATP event (release)
	j_ATP

}

INITIAL {

	cai = cinit
	IP3i = ipinit
	ca_ER = ca_ERinit
	h = hinit
	glu = gluinit
	eATP = eATPinit
	gap_cai = 0.00
	gap_IP3i = 0.00

}

BREAKPOINT {

	rates(cai,IP3i,ca_ER,h,eATP,glu,ip30)

	if (cai > cmin) {
		j_ATP = jatpmax*(cai-cmin)/(krel+cai)
	} else {
		j_ATP = 0.0
	}

	:: STATE EQUATIONS ::
	cai = cai + dt*beta*(j_IP3R - j_SERCA + j_lER - j_PCA + j_lext)
	h = h + dt*koff*(kon - (cai + kon)*h)
	ca_ER = ca_ER + dt*rvol*(j_SERCA - j_IP3R - j_lER)
	IP3i = IP3i + dt*rh*(G_ATP + G_glu) - kdeg*IP3i + pow(dt,0.5)*rand

	SOLVE diffuse METHOD sparse

	:: GAPS ::
	cai = cai + (Pca/Dca)*gap_cai
	IP3i = IP3i + (Pip3/Dip3)*gap_IP3i

}

PROCEDURE rates(cai,IP3i,ca_ER,h,eATP,glu,ip30) {
	
	:: CAI RATES ::
	j_lext = klext*(1.0-(cai/cext))
	j_PCA = v1*( pow(cai,1.7)/( pow(k1,1.7) + pow(cai,1.7) ) ) + v2*( pow(cai,4.4)/( pow(k2,4.4) + pow(cai,4.4) ) )
	j_IP3R = jip3rmax*pow( ( (cai/(cai+kc))*(IP3i/(IP3i+ki))*h ), 3)*(1.0 - (cai/ca_ER))
	j_SERCA = jsercamax*((pow(cai,2))/(pow(cai,2)+pow(kserca,2)))
	j_lER = kler*(1.0-(cai/ca_ER))

	:: IP3i RATES ::
	delta = ((kd/ka)*kdeg*ip30)/(rh-kdeg*ip30)
	pATP = (eATP/(katp + eATP))
	G_ATP = (pATP + delta)/((kd/ka)+delta+pATP)

	:: STIMULATION ::
	pglu = (pow(glu,0.7))/(pow(kglu,0.7)+pow(glu,0.7))
	G_glu = (pglu)/((kd/ka)+pglu)

}

KINETIC diffuse {
    
    : diffusion through sections

    COMPARTMENT (PI*diam*diam/4) {cai}
    LONGITUDINAL_DIFFUSION (Dca*(PI*diam*diam/4)) {cai}
    ~ cai << (-Dca*ica*PI*diam/(2*FARADAY))

    COMPARTMENT (PI*diam*diam/4) {IP3i}
    LONGITUDINAL_DIFFUSION (Dip3*(PI*diam*diam/4)) {IP3i}
    ~ IP3i << (-Dip3*iIP3*PI*diam/(2*FARADAY))

}


