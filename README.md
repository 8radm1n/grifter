# Grifter
Python library to build large scale Vagrant topologies for the networking space, but can also be used the build small scale labs for non-networking devices.

Note: Support is targeted to python 3.6+ releases.

```
*****************************************************************
This project is in beta and stability is not currently guaranteed.
Breaking API changes can be expected.
*****************************************************************
```


The main goal of this project is to build Vagrant topologies from yaml files.
As a secondary objective I would like to also generate graphviz dot files as well.
Currently only a vagrant-libvirt compatible Vagrantfile will be generated.

[![Build Status](https://travis-ci.org/bobthebutcher/grifter.svg?branch=master)](https://travis-ci.org/bobthebutcher/grifter.svg?branch=master)
[![Coverage Status](https://coveralls.io/repos/github/bobthebutcher/grifter/badge.svg?branch=master)](https://coveralls.io/github/bobthebutcher/grifter?branch=master)

#### Installation
Create and activate virtualenv.
```
mkdir ~/test && cd ~/test
python3 -m venv .venv
source .venv/bin/activate
```

Install `grifter` with `pip`
```
pip install https://github.com/bobthebutcher/grifter/archive/master.zip
```

#### Example Usage
```
grifter create guests.yml
```


#### Example Datafile
```yaml
---
guests:
  - name: "sw01"
    vagrant_box:
      name: "arista/veos"
      version: ""
      provider: "libvirt"

    ssh:
      insert_key: False

    synced_folder:
      enabled: False

    provider_config:
      nic_adapter_count: 2
      disk_bus: "ide"
      cpus: 2
      memory: 2048
      management_network_mac: ""

    interfaces:
      - name: "eth1"
        local_port: 1
        remote_guest: "sw02"
        remote_port: 1
      - name: "eth2"
        local_port: 2
        remote_guest: "sw02"
        remote_port: 2

  - name: "sw02"
    vagrant_box:
      name: "arista/veos"
      version: ""
      provider: "libvirt"

    ssh:
      insert_key: False

    synced_folder:
      enabled: False

    provider_config:
      nic_adapter_count: 2
      disk_bus: "ide"
      cpus: 2
      memory: 2048
      management_network_mac: ""

    interfaces:
      - name: "eth1"
        local_port: 1
        remote_guest: "sw01"
        remote_port: 1
      - name: "eth2"
        local_port: 2
        remote_guest: "sw01"
        remote_port: 2
```


#### Generated Vagrantfile
```ruby
# -*- mode: ruby -*-
# vi: set ft=ruby :

def get_mac(oui="28:b7:ad")
  "Generate a MAC address"
  nic = (1..3).map{"%0.2x"%rand(256)}.join(":")
  return "#{oui}:#{nic}"
end

cwd = Dir.pwd.split("/").last
username = ENV['USER']
domain_prefix = "#{username}_#{cwd}"

Vagrant.configure("2") do |config|

  config.vm.define "sw01" do |node|
    guest_name = "sw01"
    node.vm.box = "arista/veos"
    node.vm.synced_folder ".", "/vagrant", id: "vagrant-root", disabled: true

    node.ssh.insert_key = false

    node.vm.provider :libvirt do |domain|
      domain.default_prefix = "#{domain_prefix}"
      domain.cpus = 2
      domain.memory = 2048
      domain.disk_bus = "ide"
      domain.nic_adapter_count = 2
    end

    node.vm.network :private_network,
      # sw01-int1 <--> sw02-int1
      :mac => "#{get_mac()}",
      :libvirt__tunnel_type => "udp",
      :libvirt__tunnel_local_ip => "127.255.1.1",
      :libvirt__tunnel_local_port => 10001,
      :libvirt__tunnel_ip => "127.255.1.2",
      :libvirt__tunnel_port => 10001,
      :libvirt__iface_name => "eth1",
      auto_config: false

    node.vm.network :private_network,
      # sw01-int2 <--> sw02-int2
      :mac => "#{get_mac()}",
      :libvirt__tunnel_type => "udp",
      :libvirt__tunnel_local_ip => "127.255.1.1",
      :libvirt__tunnel_local_port => 10002,
      :libvirt__tunnel_ip => "127.255.1.2",
      :libvirt__tunnel_port => 10002,
      :libvirt__iface_name => "eth2",
      auto_config: false

  end
  config.vm.define "sw02" do |node|
    guest_name = "sw02"
    node.vm.box = "arista/veos"
    node.vm.synced_folder ".", "/vagrant", id: "vagrant-root", disabled: true

    node.ssh.insert_key = false

    node.vm.provider :libvirt do |domain|
      domain.default_prefix = "#{domain_prefix}"
      domain.cpus = 2
      domain.memory = 2048
      domain.disk_bus = "ide"
      domain.nic_adapter_count = 2
    end

    node.vm.network :private_network,
      # sw02-int1 <--> sw01-int1
      :mac => "#{get_mac()}",
      :libvirt__tunnel_type => "udp",
      :libvirt__tunnel_local_ip => "127.255.1.2",
      :libvirt__tunnel_local_port => 10001,
      :libvirt__tunnel_ip => "127.255.1.1",
      :libvirt__tunnel_port => 10001,
      :libvirt__iface_name => "eth1",
      auto_config: false

    node.vm.network :private_network,
      # sw02-int2 <--> sw01-int2
      :mac => "#{get_mac()}",
      :libvirt__tunnel_type => "udp",
      :libvirt__tunnel_local_ip => "127.255.1.2",
      :libvirt__tunnel_local_port => 10002,
      :libvirt__tunnel_ip => "127.255.1.1",
      :libvirt__tunnel_port => 10002,
      :libvirt__iface_name => "eth2",
      auto_config: false

  end

end
```

#### Defaults Per-Guest Type
It is possible to define default values per guest group type. Grifter will look for a
file named `guest-defaults.yml` in the following locations from the least to most preferred:
 - `/opt/grifter/`
 - `~/.grifter/`
 - `./` 

```yaml
arista/veos:
  vagrant_box:
    version: "4.20.1F"
  ssh:
    insert_key: False
  synced_folder:
    enabled: False
  provider_config:
    nic_adapter_count: 8
    disk_bus: "ide"
    cpus: 2
    memory: 2048

juniper/vsrx:
  vagrant_box:
    version: "18.1R1.9-packetmode"
  ssh:
    insert_key: False
  synced_folder:
    enabled: False
  provider_config:
    nic_adapter_count: 8
    disk_bus: "ide"
    cpus: 2
    memory: 4096
```

Group variables can be over-written by variables at the guest variable level. The values of
the group and guest variables will be merged prior to building a `Vagrantfile` with the guest
variables taking precedence over the group variables.


This means you can have a much more succinct guests variable file by reducing alot of duplication.
Here is an example of a reduced guest variable file.
```yaml
guests:
  - name: "sw01"
    vagrant_box:
      name: "arista/veos"

    provider_config:
      nic_adapter_count: 2
      management_network_mac: "00:00:00:00:00:01"

    interfaces:
      - name: "eth1"
        local_port: 1
        remote_guest: "sw02"
        remote_port: 1
      - name: "eth2"
        local_port: 2
        remote_guest: "sw02"
        remote_port: 2

  - name: "sw02"
    vagrant_box:
      name: "arista/veos"

    provider_config:
      nic_adapter_count: 2
      management_network_mac: "00:00:00:00:00:02"

    interfaces:
      - name: "eth1"
        local_port: 1
        remote_guest: "sw01"
        remote_port: 1
      - name: "eth2"
        local_port: 2
        remote_guest: "sw01"
        remote_port: 2
```

The resulting `Vagrantfile` is as follows
```ruby
# -*- mode: ruby -*-
# vi: set ft=ruby :

def get_mac(oui="28:b7:ad")
  "Generate a MAC address"
  nic = (1..3).map{"%0.2x"%rand(256)}.join(":")
  return "#{oui}:#{nic}"
end

cwd = Dir.pwd.split("/").last
username = ENV['USER']
domain_prefix = "#{username}_#{cwd}"

Vagrant.configure("2") do |config|

  config.vm.define "sw01" do |node|
    guest_name = "sw01"
    node.vm.box = "arista/veos"
    node.vm.box_version = "4.20.1F"
    node.vm.synced_folder ".", "/vagrant", id: "vagrant-root", disabled: true

    node.ssh.insert_key = false

    node.vm.provider :libvirt do |domain|
      domain.default_prefix = "#{domain_prefix}"
      domain.cpus = 2
      domain.memory = 2048
      domain.disk_bus = "ide"
      domain.management_network_mac = "00:00:00:00:00:01"
      domain.nic_adapter_count = 2
    end

    node.vm.network :private_network,
      # sw01-int1 <--> sw02-int1
      :mac => "#{get_mac()}",
      :libvirt__tunnel_type => "udp",
      :libvirt__tunnel_local_ip => "127.255.1.1",
      :libvirt__tunnel_local_port => 10001,
      :libvirt__tunnel_ip => "127.255.1.2",
      :libvirt__tunnel_port => 10001,
      :libvirt__iface_name => "eth1",
      auto_config: false

    node.vm.network :private_network,
      # sw01-int2 <--> sw02-int2
      :mac => "#{get_mac()}",
      :libvirt__tunnel_type => "udp",
      :libvirt__tunnel_local_ip => "127.255.1.1",
      :libvirt__tunnel_local_port => 10002,
      :libvirt__tunnel_ip => "127.255.1.2",
      :libvirt__tunnel_port => 10002,
      :libvirt__iface_name => "eth2",
      auto_config: false

  end
  config.vm.define "sw02" do |node|
    guest_name = "sw02"
    node.vm.box = "arista/veos"
    node.vm.box_version = "4.20.1F"
    node.vm.synced_folder ".", "/vagrant", id: "vagrant-root", disabled: true

    node.ssh.insert_key = false

    node.vm.provider :libvirt do |domain|
      domain.default_prefix = "#{domain_prefix}"
      domain.cpus = 2
      domain.memory = 2048
      domain.disk_bus = "ide"
      domain.management_network_mac = "00:00:00:00:00:02"
      domain.nic_adapter_count = 2
    end

    node.vm.network :private_network,
      # sw02-int1 <--> sw01-int1
      :mac => "#{get_mac()}",
      :libvirt__tunnel_type => "udp",
      :libvirt__tunnel_local_ip => "127.255.1.2",
      :libvirt__tunnel_local_port => 10001,
      :libvirt__tunnel_ip => "127.255.1.1",
      :libvirt__tunnel_port => 10001,
      :libvirt__iface_name => "eth1",
      auto_config: false

    node.vm.network :private_network,
      # sw02-int2 <--> sw01-int2
      :mac => "#{get_mac()}",
      :libvirt__tunnel_type => "udp",
      :libvirt__tunnel_local_ip => "127.255.1.2",
      :libvirt__tunnel_local_port => 10002,
      :libvirt__tunnel_ip => "127.255.1.1",
      :libvirt__tunnel_port => 10002,
      :libvirt__iface_name => "eth2",
      auto_config: false

  end

end
```