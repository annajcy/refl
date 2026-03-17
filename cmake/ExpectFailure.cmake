if(NOT DEFINED COMMAND_TO_RUN)
  message(FATAL_ERROR "COMMAND_TO_RUN must be provided")
endif()

execute_process(
  COMMAND ${COMMAND_TO_RUN}
  RESULT_VARIABLE command_result
)

if(command_result EQUAL 0)
  message(FATAL_ERROR "Command was expected to fail but exited successfully")
endif()
