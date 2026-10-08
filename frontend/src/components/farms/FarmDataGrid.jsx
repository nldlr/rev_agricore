import { useEffect, useState } from 'react';
import { DataGrid } from '@mui/x-data-grid';
import { Alert, Box, CircularProgress, Button, Dialog, DialogActions, DialogContent, DialogTitle, MenuItem, Stack, TextField } from '@mui/material';
import apiClient from '../../api/client.js';
import '../../App.css';

//defines our DataGrid columns and maps them to our backend API response data
const columns = [
  { field: 'id', headerName: 'ID', width: 70 },
  { field: 'name', headerName: 'Name', width: 220},
  { field: 'location_region', headerName: 'Location Region', width: 260 },
  { field: 'capacity', headerName: 'Capacity', width: 230, type: 'number'  },
  { field: 'supervisor_id', headerName: 'Supervisor ID', width: 260, type: 'number' },
];
    // id: int
    // name: str
    // location_region: str
    // capacity: int
    // supervisor_id: int


//local state variables for tracking table rows, loading status, and network errors
//to track the lifecycle of the async API request so the UI can render appropriately
function FarmDataGrid({ onSuccess }) {
  const [farms, setFarms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [formValues, setFormValues] = useState({
    serial_number: '',
    model: '',
    fuel_level: '',
    farm_id: '',
    status: 'Idle',
  });
  const [lowFuelFlag, setLowFuelFlag] = useState(false);
  const [errorFarm, setErrorFarm] = useState(null);

  //React effect hook that runs our async fetch 
  // useEffect(() => {
  //   //tracks component mount status to prevent memory leaks via network request delays
  //   let isMounted = true;

    //pulls our equipment data from our backend
    async function fetchFarms() {
      setLoading(true);
      try {
        let response;
        response = await apiClient.get('/farms');
        setFarms(response.data);
        setError(null); //make sure we clear any old errors
      } catch {
          setError('Could not load data.');
      } finally {
          setLoading(false);
      }
    }

    // fetchFarms();
    useEffect(() => {
      fetchFarms();
    }, []);

    const handleFieldChange = (field) => (event) => {
      setFormValues((prev)=> ({ ...prev, [field]: event.target.value}));
    }

  //handles the actual creation of a new equipment record in the db
//   const handleCreate = async() => {
//     setErrorFarm(null);
//     try {
//       await apiClient.post('/farms', {
//         ...formValues,
//       fuel_level: Number(formValues.fuel_level),
//       farm_id: Number(formValues.farm_id),
//     });
//     setDialogOpen(false);
//     setFormValues({serial_number: '', model: '', fuel_level: '', farm_id: '', status: 'Idle'});
//     onSuccess(`Farm ${formValues.serial_number} created.`);
//     await fetchFarms(); //see the table data refreshed with the new equipment
//     } catch (err) {
//       const msg = err.message || 'Submission failed (error unknown).';
//       setErrorFarm(msg);
//     }
//   }

  //shows a spinning progress indicator if loading data
  if (loading) return <CircularProgress />;
  //shows error alert if API call fails
  if (error) return <Alert severity="error">{error}</Alert>;

  //loads data grid component if all goes well
  return (
    <Box>
        {/* <Button variant="outlined" sx={{ mb: 2}} onClick={() => setDialogOpen(true)}>Add Farm</Button> */}
    <Box sx={{ height: 400, width: '100%' }}>
      <DataGrid rows={farms} columns={columns} getRowId={(row) => row.id} />
    </Box>

    </Box>
  );
}

export default FarmDataGrid; 