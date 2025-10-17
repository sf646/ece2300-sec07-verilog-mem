#=========================================================================
# mem
#=========================================================================

mem_srcs = \
  Mux4_4b_RTL.v \
  Decoder_2b_RTL.v \
  Register_4b_RTL.v \
  RegfileStruct1r1w_4x4b_RTL.v \
  RegfileFlat1r1w_4x4b_RTL.v \

mem_tests = \
  Mux4_4b_RTL-test.v \
  Decoder_2b_RTL-test.v \
  Register_4b_RTL-test.v \
  RegfileStruct1r1w_4x4b_RTL-test.v \
  RegfileFlat1r1w_4x4b_RTL-test.v \

$(eval $(call check_part,mem))
