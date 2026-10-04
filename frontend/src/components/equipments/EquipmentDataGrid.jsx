import { useEffect, useState } from 'react';
import { DataGrid } from '@mui/x-data-grid';
import { Alert, Box, CircularProgress, Button, Dialog, DialogActions, DialogContent, DialogTitle, MenuItem, Stack, TextField } from '@mui/material';
import apiClient from '../../api/client.js';

//defines our DataGrid columns and maps them to our backend API response data
const columns = [
  { field: 'id', headerName: 'ID', width: 70 },
  { field: 'serial_number', headerName: 'Serial Number', width: 150 },
  { field: 'model', headerName: 'Model', width: 160 },
  { field: 'fuel_level', headerName: 'Fuel %', width: 120, type: 'number' },
  { field: 'status', headerName: 'Status', width: 130 },
  { field: 'farm_id', headerName: 'Farm ID', width: 110, type: 'number' },
];

const STATUS_OPTIONS = ['Idle', 'In-Mission', 'Maintenance', 'Retired'];

//local state variables for tracking table rows, loading status, and network errors
//to track the lifecycle of the async API request so the UI can render appropriately
function EquipmentDataGrid({ onSuccess }) {
  const [equipments, setEquipments] = useState([]);
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

  //React effect hook that runs our async fetch 
  // useEffect(() => {
  //   //tracks component mount status to prevent memory leaks via network request delays
  //   let isMounted = true;

    //pulls our equipment data from our backend
    async function fetchEquipments() {
      setLoading(true);
      try {
        const response = await apiClient.get('/equipments');
        setEquipments(response.data);
        setError(null); //make sure we clear any old errors
        // if (isMounted) setEquipments(response.data);
      } catch {
        // if (isMounted)
          setError('Could not load clinical data.');
      } finally {
        // if (isMounted)
          setLoading(false);
      }
    }

    // fetchEquipments();
    useEffect(() => {
      fetchEquipments();
    }, []);

    const handleFieldChange = (field) => (event) => {
      setFormValues((prev)=> ({ ...prev, [field]: event.target.value}));
    }
  //   return () => {
  //     isMounted = false;
  //   };
  // }, []);

  //handles the actual creation of a new equipment record in the db
  const handleCreate = async() => {
    try {
      await apiClient.post('/equipments', {
        ...formValues,
      fuel_level: Number(formValues.fuel_level),
      farm_id: Number(formValues.farm_id),
    });
    setDialogOpen(false);
    setFormValues({serial_number: '', model: '', fuel_level: '', farm_id: '', status: 'Idle'});
    onSuccess(`Equipment ${formValues.serial_number} created.`);
    await fetchEquipments(); //see the table data refreshed with the new equipment
    } catch {
      //a real app would surface this inline in the dialog
    }
  }

  //shows a spinning progress indicator if loading data
  if (loading) return <CircularProgress />;
  //shows error alert if API call fails
  if (error) return <Alert severity="error">{error}</Alert>;

  //loads data grid component if all goes well
  return (
    <Box>
      <Button variant="outlined" sx={{ mb: 2}} onClick={() => setDialogOpen(true)}>Add Equipment</Button>
    <Box sx={{ height: 400, width: '100%' }}>
      <DataGrid rows={equipments} columns={columns} getRowId={(row) => row.id} />
    </Box>

    <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
      <DialogTitle>Add New Equipment</DialogTitle>
      <DialogContent>
        <Stack spacing={2} sx={{ mt: 1, minWidth: 300}}>
          <TextField label="Serial Number" value={formValues.serial_number} onChange={handleFieldChange('serial_number')} />
          <TextField label="Model" value={formValues.model} onChange={handleFieldChange('model')} />
          <TextField label="Fuel Level" type="number" value={formValues.fuel_level} onChange={handleFieldChange('fuel_level')} />
          <TextField label="Farm ID" type="number" value={formValues.farm_id} onChange={handleFieldChange('farm_id')} />
          <TextField select label="Status" value={formValues.status} onChange={handleFieldChange('status')}>
            {STATUS_OPTIONS.map((option) => (
              <MenuItem key={option} value={option}>{option}</MenuItem>
            ))}
          </TextField>
        </Stack>
      </DialogContent>
            <DialogActions>
              <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
              <Button variant="contained" onClick={handleCreate}>Create</Button>
            </DialogActions>

    </Dialog>

    </Box>
  );
}

export default EquipmentDataGrid; 