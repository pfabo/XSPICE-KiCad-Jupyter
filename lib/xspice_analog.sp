** XSPICE analog models **


.subckt A_MULT_2 in1 in2 out params: in1_gain=1 in1_offset=0 in2_gain=1 in2_offset=0 out_gain=1.0 out_offset=0
amult [in1 in2] out sigmult
.model sigmult MULT(
    + in_offset =['in1_offset' 'in2_offset']
    + in_gain   =['in1_gain' 'in2_gain']
    + out_gain  ='out_gain'
    + out_offset='out_offset')
.ends


.subckt A_SUMM_2 in1 in2 out params: in1_gain=1 in1_offset=0 in2_gain=1 in2_offset=0 out_gain=1.0 out_offset=0
asum [in1 in2] out sum2
.model sum2 SUMMER(
    +in_offset=['in1_offset' 'in2_offset']
    +in_gain=['in1_gain' 'in2_gain']
    + out_gain='out_gain'
    +out_offset='out_offset')
.ends


.subckt A_INT in out params: in_offset=0.0 out_gain=1.0 out_ic=0.0
aint in out integrator
.model integrator INT(
    + in_offset='in_offset'
    + gain='out_gain'
    + out_lower_limit=-1e12
    + out_upper_limit=1e12
    + limit_range=1e-9
    + out_ic='out_ic')
.ends


.subckt A_GAIN in out params: gain=1.0 in_offset=0.0 out_offset=0.0
again in out amp
.model amp GAIN(
    +in_offset='in_offset'
    +gain='gain'
    +out_offset='out_offset')
.ends


.subckt A_HYST in out params: hyst=0.1 in_low=-1  in_high=1 out_upper=5 out_lower=0 smooth=0.01
ahyst in out ahyst
.model ahyst HYST(
    +hyst='hyst'
    +in_low='in_low'
    +in_high='in_high'
    +out_lower_limit='out_lower'
    +out_upper_limit='out_upper'
    +input_domain='smooth'
    +fraction=TRUE)
.ends


.subckt A_LIMIT in out params: gain=1 in_offset=0 out_upper_limit=1 out_lower_limit=-1 limit_range=0.01
ahyst in out alimit
.model alimit LIMIT(
    +gain='gain'
    +in_offset='in_offset'
    +out_lower_limit='out_lower_limit'
    +out_upper_limit='out_upper_limit'
    +limit_range='limit_range'
    +fraction=TRUE)
.ends


.subckt A_CLIMIT in c_low c_high out  params: gain=1 in_offset=0  upper_delta=0 lower_delta=0 limit_range=0.01
ahyst in c_low c_high out aclimit
.model aclimit CLIMIT(
    +gain='gain'
    +in_offset='in_offset'
    +lower_delta='lower_delta'
    +upper_delta='upper_delta'
    +limit_range='limit_range'
    +fraction=TRUE)
.ends


.subckt A_RES a b params: r=100 tc1=0.0 tc2=0.0
res a b resistor
.model resistor R(
    +r='r'
    +tc1='tc1'
    +tc2='tc2')
.ends

.subckt A_CAP a b params: cap=100 tc1=0.0 tc2=0.0 ic=0.0
cap a b capacitor
.model capacitor C(
    +cap='cap'
    +tc1='tc1'
    +tc2='tc2'
    +ic='ic')
.ends


.subckt A_SWITCH control r_in r_out params: cntl_off=0.0 cntl_on=1.0 r_on=1.0 r_off=1e12
aswitch control %gd(r_in r_out) switch
.model switch ASWITCH(
    +cntl_off='cntl_off'
    +cntl_on ='cntl_on'
    +r_on    ='r_on'
    +r_off   ='r_off'
    +log     = TRUE)
.ends


.subckt A_XFER_1 in out params: gain=1.0 in_offset=0.0 a0=1.0 b1=1.0 b0=1.0
axfer1 in out transf1
.model transf1 S_XFER(
    +gain        ='gain'
    +in_offset   ='in_offset'
    +num_coeff   = [ 'a0']
    +den_coeff   = ['b1' 'b0']
    +int_ic      = [0 0]
    +denormalized_freq=6.28)
.ends


.subckt A_XFER_2 in out params: gain=1.0 in_offset=0.0 a1=1.0 a0=1.0 b2=1.0 b1=1.0 b0=1.0
axfer2 in out transf2
.model transf2 S_XFER(
    +gain        ='gain'
    +in_offset   ='in_offset'
    +num_coeff   = [ 'a1' 'a0']
    +den_coeff   = ['b2' 'b1' 'b0']
    +int_ic      = [0 0 0]
    +denormalized_freq=6.28)
.ends

