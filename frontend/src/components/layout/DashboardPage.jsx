import { Container, Typography, Box, Snackbar, Alert} from '@mui/material'
import {useState} from 'react'
import ReliabilityMetrics from '../analytics/ReliabilityMetrics.jsx'
import MaintenanceFlags from '../analytics/MaintenanceFlags.jsx'
import ReportingLines from '../analytics/ReportingLines.jsx'
import EquipmentDataGrid from '../equipments/EquipmentDataGrid.jsx'
import DiscrepancyDataGrid from '../field_jobs/DiscrepancyDataGrid.jsx'

export default function DashboardPage({ setNotification }){

  return (
    <>
      <Container maxWidth="lg" sx={{ mt: 4}}>
        <Typography variant="h5" gutterBottom>
          Agricore Dashboard
        </Typography>
        <Box sx={{ mb: 4}}>
          <EquipmentDataGrid onSuccess={setNotification}/>
        </Box>
        <Typography variant="h5"  gutterBottom>
          Co-Location Discrepancies
        </Typography>
        <Box sx={{ mb: 4}}>
          <DiscrepancyDataGrid />
        </Box>
      </Container>

      <Typography variant="h5"  gutterBottom>
      Reliability Metrics
      </Typography>
      <Box sx={{ mb: 4 }}>
      <ReliabilityMetrics />
      </Box>

      <Typography variant="h5"  gutterBottom>
      Maintenance Flags
      </Typography>
      <Box sx={{ mb: 4 }}>
      <MaintenanceFlags />
      </Box>

      <Typography variant="h5"  gutterBottom>
      Reporting Lines
      </Typography>
      <Box sx={{ mb: 4 }}>
      <ReportingLines />
      </Box>
    </>
  );
}