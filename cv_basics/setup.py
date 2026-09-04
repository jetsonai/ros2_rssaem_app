from setuptools import setup

package_name = 'cv_basics'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='nvidia',
    maintainer_email='nvidia@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
           'webcam_pub = cv_basics.webcam_pub:main',
      	   'webcam_sub = cv_basics.webcam_sub:main',
      	   'cam_node = cv_basics.cam_node:main',
           'webcam_comp_pub = cv_basics.webcam_comp_pub:main',
        ],
    },
)
