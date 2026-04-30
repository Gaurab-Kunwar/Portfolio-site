from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy

# Create the Flask app
app = Flask(__name__)

# Tell Flask where the database file will live
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///portfolio.db"

# Create the database object
db = SQLAlchemy(app)

# Define a Project table in the database
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    tech = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tech": self.tech
        }

# Create the database and tables
with app.app_context():
    db.create_all()

@app.route("/home")
@app.route("/")
def home():
    return render_template("home.html")
# GET all projects
@app.route("/projects")
def get_projects():
    projects = Project.query.all()
    return render_template("projects.html", projects=projects)

# POST - add a new project
@app.route("/projects", methods=["POST"])
def add_project():
    data = request.get_json()
    new_project = Project(
        name=data["name"],
        description=data["description"],
        tech=data["tech"]
    )
    db.session.add(new_project)
    db.session.commit()
    return jsonify(new_project.to_dict()), 201

# DELETE a project
@app.route("/projects/<int:id>", methods=["DELETE"])
def delete_project(id):
    project = Project.query.get(id)
    db.session.delete(project)
    db.session.commit()
    return jsonify({"message": "Project deleted"})

if __name__ == "__main__":
    app.run(debug=True)