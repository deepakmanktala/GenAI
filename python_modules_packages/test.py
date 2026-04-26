from custom_package import my_maths

from custom_package.subpackage import multi

from custom_package.subpackage.multi import multiply, divide

print(my_maths.addition(7,10))
print(my_maths.subtraction(90,60))

print(multi.divide(10,5))
print(multi.multiply(90,10))