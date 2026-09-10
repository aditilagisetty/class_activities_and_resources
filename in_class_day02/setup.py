from setuptools import find_packages, setup

package_name = 'in_class_day02'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='aditilagisetty',
    maintainer_email='lagisettyaditi@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'send_message = in_class_day02.send_message:main',
            'receive_message = in_class_day02.receive_message:main',
        ],
    },
)
