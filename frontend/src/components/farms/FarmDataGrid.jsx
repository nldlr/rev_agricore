import { useEffect, useState } from 'react';
import { DataGrid } from '@mui/x-data-grid';
import { Alert, Box, CircularProgress, Button, Dialog, DialogActions, DialogContent, DialogTitle, MenuItem, Stack, TextField, Icon } from '@mui/material';
import apiClient from '../../api/client.js';
import IconButton from '@mui/material/IconButton';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import '../../App.css';

//local state variables for tracking table rows, loading status, and network errors
//to track the lifecycle of the async API request so the UI can render appropriately
function FarmDataGrid({ onSuccess }) {
  const [farms, setFarms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [formValues, setFormValues] = useState({
    name: '',
    location_region: '',
    capacity: '',
    supervisor_id: '',
  });
  const [errorFarm, setErrorFarm] = useState(null);
  const [editingId, setEditingId] = useState(null); // null if creating new farm, number if updating a row

    //defines our DataGrid columns and maps them to our backend API response data
  const columns = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'name', headerName: 'Name', width: 220},
    { field: 'location_region', headerName: 'Location Region', width: 220 },
    { field: 'capacity', headerName: 'Capacity', width: 170, type: 'number'  },
    { field: 'supervisor_id', headerName: 'Supervisor ID', width: 170, type: 'number' },
    { field: 'actions', headerName: '', width: 110, disableColumnMenu: true,
      renderCell: (params) => (
        <>
          <IconButton onClick={() => handleStartEdit(params.row)}>
            <EditIcon>
            </EditIcon>
          </IconButton>
          <IconButton onClick={() => handleDelete(params.row.id)}>
            <DeleteIcon>
            </DeleteIcon>
          </IconButton>
        </>
        
      )
    },
  ];

    // id: int
    // name: str
    // location_region: str
    // capacity: int
    // supervisor_id: int


  //pulls our farm data from our backend
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


  //handles the actual creation of a new farm record in the db
  const handleCreate = async() => {
    setErrorFarm(null);
    try {
      await apiClient.post('/farms', {
        ...formValues,
      capacity: Number(formValues.capacity),
      supervisor_id: Number(formValues.supervisor_id),
      });
      setDialogOpen(false);
      setFormValues({name: '', location_region: '', capacity: '', supervisor_id: ''});
      onSuccess(`Farm ${formValues.name} created.`);
      await fetchFarms(); //see the table data refreshed with the new farm
    } catch (err) {
      const msg = err.message || 'Submission failed (error unknown).';
      setErrorFarm(msg);
    }
  }

  // prefill editing form with existing values, so user can just change what they want
  const handleStartEdit = (row) => {
    setEditingId(row.id);
    setFormValues({
      name: row.name || '',
      location_region: row.location_region || '',
      capacity: row.capacity ?? '',
      supervisor_id: row.supervisor_id ?? '',
    });
    setDialogOpen(true);
  }

  //handles updating an farm record in the db
  const handleUpdate = async() => {
    setErrorFarm(null);
    try {
      await apiClient.patch(`/farms/${editingId}`, {
        ...formValues,
        capacity: Number(formValues.capacity),
        supervisor_id: Number(formValues.supervisor_id),
      });
      setDialogOpen(false);
      setEditingId(null);
      setFormValues({name: '', location_region: '', capacity: '', supervisor_id: ''});
      onSuccess(`Farm ${formValues.name} updated.`);
      await fetchFarms(); //see the table data refreshed with the new farm
    } catch (err) {
      const msg = err.message || 'Submission failed (error unknown).';
      setErrorFarm(msg);
    }
  }

  //handles deletion of an farm record in the db
  const handleDelete = async(id) => {
    setErrorFarm(null);
    const confirmed = window.confirm(`Delete farm #${id}?`)
    if (!confirmed) return;

    try {
      await apiClient.delete(`/farms/${id}`);
      onSuccess(`Farm #${id} deleted.`);
      await fetchFarms(); //see the table data refreshed with the new farm
    } catch (err) {
      const msg = err.message || 'Submission failed (error unknown).';
      setErrorFarm(msg);
    }
  }

  //shows a spinning progress indicator if loading data
  if (loading) return <CircularProgress />;
  //shows error alert if API call fails
  if (error) return <Alert severity="error">{error}</Alert>;

  //loads data grid component if all goes well
  return (
    <Box>
      <Box id="farm_btn_box">
        <Button id="add_farm_btn" variant="outlined" sx={{ mb: 2}} onClick={() => setDialogOpen(true)}>Add Farm</Button>
      </Box>
    <Box sx={{ height: 400, width: '100%' }}>
      <DataGrid rows={farms} columns={columns} getRowId={(row) => row.id} />
    </Box>

    <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
      <DialogTitle sx={{color: 'black'}}>{editingId ? `Edit Farm` : 'Add New Farm'}</DialogTitle>
      <DialogContent>
        <Stack spacing={2} sx={{ mt: 1, minWidth: 300}}>
          <TextField label="Name" value={formValues.name} onChange={handleFieldChange('name')} />
          <TextField label="Location Region" value={formValues.location_region} onChange={handleFieldChange('location_region')} />
          <TextField label="Capacity" type="number" value={formValues.capacity} onChange={handleFieldChange('capacity')} />
          <TextField label="Supervisor Id" type="number" value={formValues.supervisor_id} onChange={handleFieldChange('supervisor_id')} />
        </Stack>
      </DialogContent>
            <DialogActions>
              <Button onClick={() => {
                if (editingId !== null) {setFormValues({name: '', location_region: '', capacity: '', supervisor_id: ''});};
                setDialogOpen(false)
              }}>Cancel</Button>
              <Button variant="contained" onClick={editingId ? handleUpdate : handleCreate}>
                {editingId ? 'Update' : 'Create'}
              </Button>
              {errorFarm && (<Alert severity="error">{errorFarm}</Alert>)}
            </DialogActions>

    </Dialog>

    </Box>
  );
}

export default FarmDataGrid; 