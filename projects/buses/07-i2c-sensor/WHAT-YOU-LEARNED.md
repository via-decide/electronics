# What You Learned

I2C is not a library call. SDA and SCL are shared open-drain lines whose rise time comes from pull-ups and bus capacitance.

Completion proof: Firmware shows at least one raw register transaction without a sensor abstraction library.
