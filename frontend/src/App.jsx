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

import DashboardPage from './components/layout/DashboardPage.jsx'
import FarmsPage from './components/layout/FarmsPage.jsx'
import FieldJobsPage from './components/layout/FieldJobsPage.jsx'
import ServiceReportsPage from './components/layout/ServiceReportsPage.jsx'


//a main dashboard component that renders the application header and equipment data grid to authenticated users
function Dashboard(){
  //stores the current user object and logout function from the global AuthContext
  const {user, logout} = useAuth()
  const [notification, setNotification] = useState(null)
  const [currentPage, setCurrentPage] = useState('Dashboard');

  const renderPage = () => {
    switch (currentPage) {
      case 'Dashboard':
        return <DashboardPage setNotification={setNotification}/>;
      case 'Farms':
        return <FarmsPage setNotification={setNotification}/>;
      case 'FieldJobs':
        return <FieldJobsPage setNotification={setNotification}/>;
      case 'ServiceReports':
        return <ServiceReportsPage setNotification={setNotification}/>; // Skipping Equipments page since it already appears on dashboard.
      default:
        return <p>Page Error!</p>;
    }
  }


  return (
    <>
      <AppHeader currentPage={currentPage} setCurrentPage={setCurrentPage} username={user?.sub} role={user?.role} onLogout={logout} />

      <Container maxWidth="lg" sx={{ mt: 4}}>
        {renderPage()}
      </Container>

      <Snackbar
        open={Boolean(notification)}
        autoHideDuration={4000}
        onClose={() => setNotification(null)}>
          <Alert severity="success" onClose={() => setNotification(null)}>
            {notification}
          </Alert>
        </Snackbar>
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