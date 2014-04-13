class requirements {
      exec { 'apt-get update':
              command => '/usr/bin/apt-get update',}
      package{ 'python-pip':
                ensure=>'present',
                require => Exec['apt-get update'],}
      package{ 'puppet-pip':
                ensure=>'present',
                provider => 'gem',
                require => Package['python-pip'],}
      package{ 'django==1.4':
                ensure=>'present',
                provider => 'pip',
                require => Package['puppet-pip'],}
}
