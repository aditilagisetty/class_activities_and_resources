from setuptools import find_packages, setup

package_name = 'in_class_day03'

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
            'emergency_stop = in_class_day03.emergency_stop:main',
            'distance_emergency_stop = in_class_day03.distance_emergency_stop:main',
            'safe_teleop = in_class_day03.safe_teleop:main',
            'arrow_teleop = in_class_day03.arrow_teleop:main'
        ],
    },
)
