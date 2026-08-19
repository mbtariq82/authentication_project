# Resource Group - Container for all resources
resource "azurerm_resource_group" "main" {
  name       = "auth-${var.environment}-rg"
  location   = var.location
}

# Virtual Network - Network container
resource "azurerm_virtual_network" "main" {
  name                = "auth-${var.environment}-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
}

# Public Subnet - For FastAPI VM
resource "azurerm_subnet" "public" {
  name                 = "auth-public-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.1.0/24"]
}

# Network Security Group - Firewall rules
resource "azurerm_network_security_group" "app" {
  name                = "auth-${var.environment}-nsg"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  security_rule {
    name                       = "AllowAdminSSH"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = var.admin_ip
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "AllowHTTP"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "AllowFastAPI"
    priority                   = 120
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "8000"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

# Associate NSG with subnet
resource "azurerm_subnet_network_security_group_association" "public" {
  subnet_id                 = azurerm_subnet.public.id
  network_security_group_id = azurerm_network_security_group.app.id
}

# Public IP - Static IP for VM
resource "azurerm_public_ip" "fastapi" {
  name                = "auth-fastapi-pip"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  allocation_method   = "Static"
  sku                 = "Standard"
}

# Network Interface - Attach VM to subnet
resource "azurerm_network_interface" "fastapi" {
  name                = "auth-fastapi-nic"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "testconfig"
    subnet_id                     = azurerm_subnet.public.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.fastapi.id
  }
}

# Attach NSG to NIC
resource "azurerm_network_interface_security_group_association" "fastapi" {
  network_interface_id      = azurerm_network_interface.fastapi.id
  network_security_group_id = azurerm_network_security_group.app.id
}

# Linux VM - For FastAPI application
resource "azurerm_linux_virtual_machine" "fastapi" {
  name                = "auth-fastapi-vm"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  admin_username = "azureuser"

  admin_ssh_key {
    username   = "azureuser"
    public_key = file("~/.ssh/id_rsa.pub")
  }

  network_interface_ids = [azurerm_network_interface.fastapi.id]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts-gen2"
    version   = "latest"
  }

  size = "Standard_B1s"

  user_data = base64encode(file("${path.module}/user_data.sh"))
}

# PostgreSQL Database
resource "azurerm_postgresql_flexible_server" "main" {
  name                   = "auth-postgres-${var.environment}"
  location               = azurerm_resource_group.main.location
  resource_group_name    = azurerm_resource_group.main.name
  version                = "14"
  administrator_login    = "dbadmin"
  administrator_password = var.db_password

  sku_name   = "B_Standard_B1ms"
  storage_mb = 20480

  public_network_access_enabled = true

  depends_on = [azurerm_resource_group.main]
}

resource "azurerm_postgresql_flexible_server_database" "main" {
  name            = "authentication"
  server_id       = azurerm_postgresql_flexible_server.main.id
  charset         = "utf8"
  collation       = "en_US.utf8"
}
