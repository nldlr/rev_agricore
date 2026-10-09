import { AppBar, Toolbar, Typography, Box, Button, IconButton, Menu, MenuItem, ListItemIcon, ListItemText } from '@mui/material';
import PrecisionManufacturingIcon from '@mui/icons-material/PrecisionManufacturing';
import MenuIcon from '@mui/icons-material/Menu';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import LightModeIcon from '@mui/icons-material/LightMode';
import {useState} from 'react'
import { useColorMode } from '../../main';

function AppHeader({currentPage, setCurrentPage, username, role, onLogout}) {
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);
  const { mode, toggleColorMode } = useColorMode();

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handlePageSelect = (page) => {
    setCurrentPage(page);
    handleMenuClose();
  };


  return (
    <AppBar position="static" sx={{ 
        backgroundColor: mode === 'dark' ? 'secondary.main' : 'primary.main' 
      }}>
      <Toolbar sx={{ display: 'flex', alignItems: 'center', gap: 2}}>
        
        {/* Hamburger Menu Icon */}
        <IconButton
          size="large"
          edge="start"
          color="inherit"
          aria-label="menu"
          onClick={handleMenuOpen}
          sx={{ mr: 1 }}
        >
          <MenuIcon />
        </IconButton>

        {/* Dropdown Menu */}
        <Menu
          id="navigation-menu"
          anchorEl={anchorEl}
          open={open}
          onClose={handleMenuClose}
        >
          <MenuItem 
            selected={currentPage === 'Dashboard'} 
            onClick={() => handlePageSelect('Dashboard')}
          >
            <ListItemText>Dashboard</ListItemText>
          </MenuItem>
          
          <MenuItem 
            selected={currentPage === 'Farms'} 
            onClick={() => handlePageSelect('Farms')}
          >
            <ListItemText>Farms</ListItemText>
          </MenuItem>

          <MenuItem 
            selected={currentPage === 'FieldJobs'} 
            onClick={() => handlePageSelect('FieldJobs')}
          >
            <ListItemText>Field Jobs</ListItemText>
          </MenuItem>

          <MenuItem 
            selected={currentPage === 'ServiceReports'} 
            onClick={() => handlePageSelect('ServiceReports')}
          >
            <ListItemText>Service Reports</ListItemText>
          </MenuItem>

          <MenuItem 
            selected={currentPage === 'Users'} 
            onClick={() => handlePageSelect('Users')}
          >
            <ListItemText>Users</ListItemText>
          </MenuItem>
        </Menu>




        <PrecisionManufacturingIcon sx={{ mr: 2 }} />
        <Typography variant="h6" component="h1">
          Agricore Command Center
        </Typography>

        <IconButton color="inherit" onClick={toggleColorMode} aria-label="toggle light/dark theme">
          {mode === 'dark' ? <DarkModeIcon /> : <LightModeIcon />}
        </IconButton>

        {username && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2}}>
            <Typography variant="body2">{username}({role})</Typography>
            <Button color="inherit" onClick={onLogout}>Log Out</Button>
          </Box>
        )}

      </Toolbar>
    </AppBar>
  );
}

export default AppHeader;