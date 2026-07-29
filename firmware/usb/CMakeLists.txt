add_library(usb_service usb_service.c)
target_include_directories(usb_service PUBLIC include)
target_link_libraries(usb_service PUBLIC storage)
target_compile_options(usb_service PRIVATE -Wall -Wextra -Wpedantic -Werror)

add_executable(usb_service_host_tests tests/host/test_usb_service_negative.c)
target_link_libraries(usb_service_host_tests PRIVATE usb_service)
target_compile_options(usb_service_host_tests PRIVATE -Wall -Wextra -Wpedantic -Werror)
add_test(NAME usb_service_host_tests COMMAND usb_service_host_tests)
