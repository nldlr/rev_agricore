import { Container, Typography, Box, Snackbar, Alert} from '@mui/material'
import {useState} from 'react'
import AppHeader from './components/layout/AppHeader.jsx'

import ReliabilityMetrics from './components/analytics/ReliabilityMetrics.jsx'
import MaintenanceFlags from './components/analytics/MaintenanceFlags.jsx'
import ReportingLines from './components/analytics/ReportingLines.jsx'

import LoginForm from './components/auth/LoginForm.jsx';
import EquipmentDataGrid from './components/equipments/EquipmentDataGrid.jsx';
import DiscrepancyDataGrid from './components/field_jobs/DiscrepancyDataGrid.jsx';
import ServiceReportDataGrid from './components/service_reports/ServiceReportDataGrid.jsx';
import FieldJobDataGrid from './components/field_jobs/FieldJobDataGrid.jsx';
import FarmDataGrid from './components/farms/FarmDataGrid.jsx';
import { AuthProvider, useAuth } from './context/AuthContext.jsx';

//a main dashboard component that renders the application header and equipment data grid to authenticated users
function Dashboard(){
  //stores the current user object and logout function from the global AuthContext
  const {user, logout} = useAuth()
  const [notification, setNotification] = useState(null)

  return (
    <>
      <AppHeader username={user?.sub} role={user?.role} onLogout={logout} />
      <Container maxWidth="lg" sx={{ mt: 4}}>
        <Typography variant="h5" component="h2" gutterBottom>
          Agricore Overview
        </Typography>
        <Box sx={{ mb: 4}}>
          <EquipmentDataGrid onSuccess={setNotification}/>
        </Box>
        <Typography variant="h5" component="h2" gutterBottom>
          Co-Location Discrepancies
        </Typography>
        <Box sx={{ mb: 4}}>
          <DiscrepancyDataGrid />
        </Box>
      </Container>

      <Typography variant="h5" component="h2" gutterBottom>
      Reliability Metrics
      </Typography>
      <Box sx={{ mb: 4 }}>
      <ReliabilityMetrics />
      </Box>

      <Typography variant="h5" component="h2" gutterBottom>
      Maintenance Flags
      </Typography>
      <Box sx={{ mb: 4 }}>
      <MaintenanceFlags />
      </Box>

      <Typography variant="h5" component="h2" gutterBottom>
      Reporting Lines
      </Typography>
      <Box sx={{ mb: 4 }}>
      <ReportingLines />
      </Box>

      <Snackbar
        open={Boolean(notification)}
        autoHideDuration={4000}
        onClose={() => setNotification(null)}>
          <Alert severity="success" onClose={() => setNotification(null)}>
            {notification}
          </Alert>
        </Snackbar>

      <Container maxWidth="lg" sx={{ mt: 4}}>
        <Typography variant="h5" component="h2" gutterBottom>
          Farms
        </Typography>
        <Box sx={{ mb: 4}}>
          <FarmDataGrid onSuccess={setNotification}/>
        </Box>
        <Typography variant="h5" component="h2" gutterBottom>
          Field Jobs
        </Typography>
        <Box sx={{ mb: 4}}>
          <FieldJobDataGrid onSuccess={setNotification}/>
        </Box>
        <Typography variant="h5" component="h2" gutterBottom>
          Service Reports
        </Typography>
        <Box sx={{ mb: 4}}>
          <ServiceReportDataGrid onSuccess={setNotification}/>
        </Box>
      </Container>

    </>
  );
}

//conditional layout switcher component that renders either the Dashboard or the login form
//based on the user's authentication status, tracked in the global AuthContext
function AppContent() {
  const {isAuthenticated } = useAuth();
  return isAuthenticated ? <Dashboard /> : <LoginForm />;
}

//acts as a root application component that wraps the entire app in the AuthProvider context
function App(){
  return (
      <AuthProvider>
        <AppContent />
      </AuthProvider>
  )
}

export default App;