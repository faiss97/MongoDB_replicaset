import subprocess

def test_rs_status():
    cmd = ["bash", "-lc", "mongosh --quiet --eval 'try { rs.status() } catch(e) { print(e) }'"]
    cp = subprocess.run(cmd, capture_output=True, text=True)
    assert cp.returncode == 0
