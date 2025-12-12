import streamlit as st
from solid2 import scad_render
import cad_library as cl
import subprocess
import os
import streamlit_stl

st.set_page_config(page_title="Parametric CAD Modeler", layout="wide")

st.title("RVCE Parametric Modeler")
st.markdown("Select a component from the sidebar and adjust parameters to generate SCAD code.")

# Sidebar for Component Selection
st.sidebar.header("Design Parameters")


component_type = st.sidebar.selectbox(
    "Select Component",
    ["Bolt", "Flange", "Nut", "Washer", "L-Bracket"]
)

st.sidebar.markdown(f"### {component_type} Parameters")

generated_obj = None

# Dynamic Inputs based on selection
if component_type == "Bolt":
    head_radius = st.sidebar.slider("Head Radius", min_value=1.0, max_value=50.0, value=10.0)
    head_height = st.sidebar.slider("Head Height", min_value=1.0, max_value=50.0, value=5.0)
    bolt_radius = st.sidebar.slider("Bolt Radius", min_value=1.0, max_value=30.0, value=5.0)
    bolt_length = st.sidebar.slider("Bolt Length", min_value=5.0, max_value=200.0, value=30.0)
    
    generated_obj = cl.create_bolt(head_radius, head_height, bolt_radius, bolt_length)

elif component_type == "Flange":
    flange_radius = st.sidebar.slider("Flange Radius", min_value=10.0, max_value=200.0, value=50.0)
    pipe_radius = st.sidebar.slider("Pipe Radius", min_value=5.0, max_value=100.0, value=20.0)
    thickness = st.sidebar.slider("Thickness", min_value=1.0, max_value=50.0, value=5.0)
    num_holes = st.sidebar.slider("Number of Holes", min_value=3, max_value=20, value=6)
    
    if pipe_radius >= flange_radius:
        st.error("Invalid Parameters: Pipe Radius must be smaller than Flange Radius.")
    else:
        generated_obj = cl.create_flange(flange_radius, pipe_radius, thickness, num_holes)

elif component_type == "Nut":
    inner_radius = st.sidebar.slider("Inner Radius", min_value=1.0, max_value=50.0, value=5.0)
    outer_radius = st.sidebar.slider("Outer Radius", min_value=2.0, max_value=60.0, value=10.0)
    thickness = st.sidebar.slider("Thickness", min_value=1.0, max_value=50.0, value=5.0)
    
    if inner_radius >= outer_radius:
        st.error("Invalid Parameters: Inner Radius must be smaller than Outer Radius.")
    else:
        generated_obj = cl.create_nut(inner_radius, outer_radius, thickness)

elif component_type == "Washer":
    inner_radius = st.sidebar.slider("Inner Radius", min_value=1.0, max_value=50.0, value=5.0)
    outer_radius = st.sidebar.slider("Outer Radius", min_value=2.0, max_value=60.0, value=12.0)
    thickness = st.sidebar.slider("Thickness", min_value=0.5, max_value=20.0, value=2.0)
    
    if inner_radius >= outer_radius:
        st.error("Invalid Parameters: Inner Radius must be smaller than Outer Radius.")
    else:
        generated_obj = cl.create_washer(inner_radius, outer_radius, thickness)

elif component_type == "L-Bracket":
    length = st.sidebar.slider("Length", min_value=5.0, max_value=200.0, value=50.0)
    width = st.sidebar.slider("Width", min_value=5.0, max_value=100.0, value=20.0)
    height = st.sidebar.slider("Height", min_value=5.0, max_value=200.0, value=40.0)
    thickness = st.sidebar.slider("Thickness", min_value=1.0, max_value=20.0, value=5.0)
    
    generated_obj = cl.create_bracket(length, width, height, thickness)

# Generate and Display SCAD Code
@st.cache_data(show_spinner=False)
def generate_stl_content(scad_code, scad_path):
    with open("temp.scad", "w") as f:
        f.write(scad_code)
    
    if not os.path.exists(scad_path):
        raise FileNotFoundError("OpenSCAD executable not found at specified path.")

    subprocess.run(
        [scad_path, "-o", "temp.stl", "temp.scad"],
        check=True,
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL
    )
    
    if os.path.exists("temp.stl"):
        with open("temp.stl", "rb") as f:
            return f.read()
    return None

if generated_obj:
    scad_code = scad_render(generated_obj)
    
    tab1, tab2, tab3 = st.tabs(["🖼️ 3D Preview", "📝 Source Code", "⚙️ Settings"])

    with tab3:
        st.markdown("Only change this if the preview is not working. Default path: C:/Program Files/OpenSCAD/openscad.exe")
        openscad_path = st.text_input(
            "OpenSCAD Executable Path",
            value=r"C:\Program Files (x86)\OpenSCAD\openscad.exe" 
        )

    with tab1:
        # 3D Preview Generation
        try:
            with st.spinner("Hang on just there! Generating 3D Model... 🚀"):
                stl_data = generate_stl_content(scad_code, openscad_path)
            
            if stl_data:
                # write to a temp file for the component to read
                # We reuse a single filename to avoid disk clutter, but since we have the data, we write it fresh.
                with open("preview_cache.stl", "wb") as f:
                    f.write(stl_data)
                    
                streamlit_stl.stl_from_file("preview_cache.stl", height=500)
            else:
                 st.warning("STL Generation produced no output.")
                
        except (FileNotFoundError, OSError) as e:
            st.warning(f"Preview unavailable: {e}. Please check the OpenSCAD path in the sidebar.")
        except subprocess.CalledProcessError:
            st.warning("Preview generation failed. OpenSCAD encountered an error.")
        except Exception as e:
            st.warning(f"An error occurred during preview generation: {e}")

    with tab2:
        st.text_area("Copy this code into OpenSCAD:", value=scad_code, height=400)
    
    st.download_button(
        label="Download .scad file",
        data=scad_code,
        file_name="my_design.scad",
        mime="text/plain"
    )
    
else:
    # If explicitly None (validation failed), warning might be enough, but if it was initial state or error..
    # Since we show specific errors above, we can just pass here or show a generic instruction if needed.
    # But the 'else' block from before was 'Error generating geometry'.
    # If we failed validation, we don't want to show that generic error if we already showed a specific one.
    # So we can keep it simple: if generated_obj is None and no error was shown (initial state?), strictly speaking we initialize generated_obj = None.
    # But Streamlit reruns the script. So valid/invalid is determined each run.
    pass
